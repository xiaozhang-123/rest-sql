import _ from "lodash";
import {
  resultsToDataFrames,
  DataQueryRequest,
  DataQueryResponse,
  MutableDataFrame,
} from "@grafana/data";

/**
 * query函数删除了很多没用的代码。包括timeshift,将请求的时间格式统一
 *
 */
export class RestSqlDatasource {

  /*
    query(option): panel查询数据
    testDatasource(): 数据源页面验证数据源可用
    annotationQuery(options): dashboard获取注释信息
    metricFindQuery(options): 查询编辑页面获取提示信息
  */

  constructor(instanceSettings, $q, backendSrv, templateSrv) {
    console.log("------ DataSource ------");
    console.log("instanceSettings: ", instanceSettings);
    console.log("backendSrv: ", backendSrv);
    console.log("templateSrv: ", templateSrv);
    console.log("------ DataSource ------");
    this.type = instanceSettings.type;
    this.url = instanceSettings.url;
    console.log("url:" + this.url);
    this.name = instanceSettings.name;
    this.q = $q;
    this.backendSrv = backendSrv;
    this.templateSrv = templateSrv;
    this.withCredentials = instanceSettings.withCredentials;
    this.headers = {'Content-Type': 'application/json'};
    if (typeof instanceSettings.basicAuth === 'string' && instanceSettings.basicAuth.length > 0) {
      this.headers['Authorization'] = instanceSettings.basicAuth;
    }
  }

  isJson(inputStr) {
    try {
      if (typeof JSON.parse(inputStr) === "object") {
        return true;
      }
    } catch (e) {
    }
    return false;
  }


  async query(options) {
    console.log("grafana debug: Original Options: ", options);
    if (options.targets.length <= 0) {
      return this.q.when({data: []});
    }
    const data = options.targets.map(target => { //使用新版的异步api，（分别对每一个target进行异步请求，最后再集成一个统一返回
          if (target.query == null || target.query == undefined) {
            return this.q.when({data: []})
          }
          console.log("query");
          //添加时间间隔
          const singleQuery = target.query;
          if (typeof singleQuery === "object") {
            // 这里统一了时间格式为yy:MM:dd hh:mm:ss,并将起始时间都加上timeShift值
            const timeShift = parseInt(target.query.time.timeShift);
            const timeFromOrig = new Date(options.range.from.valueOf() + timeShift);
            console.log("timeFromOrig:" + timeFromOrig)
            const timeFrom = `${timeFromOrig.getFullYear().toString().padStart(4, '0')}-${(timeFromOrig.getMonth() + 1).toString().padStart(2, '0')}-${timeFromOrig.getDate().toString().padStart(2, '0')} ${timeFromOrig.getHours().toString().padStart(2, '0')}:${timeFromOrig.getMinutes().toString().padStart(2, '0')}:${timeFromOrig.getSeconds().toString().padStart(2, '0')}`;
            const timeToOrig = new Date(options.range.to.valueOf() + timeShift)
            const timeTo = `${timeToOrig.getFullYear().toString().padStart(4, '0')}-${(timeToOrig.getMonth() + 1).toString().padStart(2, '0')}-${timeToOrig.getDate().toString().padStart(2, '0')} ${timeToOrig.getHours().toString().padStart(2, '0')}:${timeToOrig.getMinutes().toString().padStart(2, '0')}:${timeToOrig.getSeconds().toString().padStart(2, '0')}`;
            console.log("timeFrom:" + timeFrom)
            singleQuery.time.begin = timeFrom;
            singleQuery.time.end = timeTo;
            // 进行variables替换
            this.replace_variables(singleQuery, timeFrom, timeTo)
          }
          let tempresult = {};
          $.ajax({ //在这个异步请求域内，不能使用原来的dorequest的promise异步方法，异步再嵌套异步，容易出现问题 ,自定义一个同步方法
            type: "post",
            url: this.url + '/query',
            data: JSON.stringify(singleQuery),
            async: false,//同步请求，未返回，会进行阻塞
            dataType: "json",
            success: function (result) {
              if (result.status === "ok") {
                tempresult = result.data;
              } else {
                console.log(result.msg);
              }

            },
            failure: function (result) {
              console.log("some failure:" + result.msg)
            }
          });
          console.log("resultresult")
          console.log(tempresult)
          return new MutableDataFrame(
              tempresult
          ) //新api 要求返回格式 ，该返回需要有一个明确，非异步未处理完的对象
        }
    );
    return {data};
  }

  replace_variables(singleQuery, timeFrom, timeTo) {
    /**
     * 说明: 1. 变量名仅支持大小写，其他字符无法识别
     *      2. 两个特殊的时间变量 $__timeFrom ,$__timeTo 分别对应用户所选时间的起止
     *      3. 可以一次使用多个变量
     *      4. 多选时为数组形式替换
     * param: singleQuery:query请求体内容
     * return: 将where部分variables进行替换后的query请求
     */
    const variables = {};
    this.templateSrv.variables.forEach(ele => {
      const key = "$" + ele.name;
      variables[key] = ele.current.value;
    });
    console.log("variables:" + variables)
    const filters = singleQuery["where"]
    filters.map((item) => {
      if (typeof item["value"] !== "number") { // todo: warning: 每次只能匹配到一个值，但是后面又用循环处理
        const varList = item["value"].match(/\$(__)*[a-zA-Z]+/g);
        console.log("DEBUG: replace_variables", varList);
        if (varList) {
          varList.forEach((varItem) => {
            if (Object.keys(variables).includes(varItem)) {
              let varValue = variables[varItem];
              console.log("varValue:" + varValue);
              if (Array.isArray(varValue) && varValue.length > 1) {
                // 变量多选时，变量值为Array
                item["value"] = varValue
              } else {
                item["value"] = item["value"].replace(varItem, varValue);
              }
            } else if (["$__timeFrom"].includes(varItem)) {
              item["value"] = item["value"].replace(varItem, `${timeFrom}`);
            } else if (["$__timeTo"].includes(varItem)) {
              item["value"] = item["value"].replace(varItem, `${timeTo}`);
            }
          });
        }
      }
    });
  }

  testDatasource() {
    return this.doRequest({
      url: this.url + '/',
      method: 'GET',
    }).then(response => {
      if (response.status === 200) {
        return {status: "success", message: "Restsql server is ready!", title: "Success"};
      }
    });
  }

  metricFindQuery(query) {
    /**
     * 发送变量的编辑内容，获取到变量的值
     */
    const payload = {
      "target": this.templateSrv.replace(query, null, 'regex')
    };

    console.log("metricFindQuery", payload);

    return this.doRequest({
      url: this.url + '/search',
      data: payload,
      method: 'POST',
    }).then((resp) => {
      if (resp && resp.data && resp.data.status === "error") {
        return Promise.reject(new Error(resp.data.msg));
      } else if (resp && resp.data && resp.data.status === "ok") {
        return this.mapToTextValue(resp.data);
      } else {
        return [];
      }
    });
  }

  metricFindOption(tableName) {
    const payload = {
      tableName
    }
    return this.doRequest({
      url: this.url + '/find_options',
      method: 'POST',
      data: payload
    }).then((resp) => {
      if (resp.data.status === "error") {
        return Promise.reject(new Error(resp.data.msg));
      } else if (resp.data.status === "ok") {
        return resp.data;
      }
    });
  }

  metricFindTables() {
    return this.doRequest({
      url: this.url + '/find_tables',
      method: 'GET',
    }).then((resp) => {
      if (resp.data.status === "error") {
        return Promise.reject(new Error(resp.data.msg));
      } else if (resp.data.status === "ok") {
        return resp.data;
      }
    });
  }

  mapToTextValue(result) {
    /**
     * 用于metricFindQuery调整下拉选框
     */
    console.log('metricFindQuery received: ', result);
    return _.map(result.data, (d, i) => {
      if (d && d.text && d.value) {
        return {text: d.text, value: d.value};
      } else if (_.isObject(d)) {
        return {text: d, value: i};
      }
      return {text: d, value: d};
    });
  }

  doRequest(options) {
    options.withCredentials = this.withCredentials;
    options.headers = this.headers;
    return this.backendSrv.datasourceRequest(options).then((response) => {
      return response
    }) //此处额外在then中进行返回，防止上层函数调用doRequest使用then出现undefined问题
  }

}
