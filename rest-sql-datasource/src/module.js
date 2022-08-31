import { RestSqlConfigCtrl } from './config_ctrl';
import {RestSqlDatasource} from './datasource';
import { RestSqlDatasourceQueryCtrl } from './query_ctrl';

class RestSqlQueryOptionsCtrl {}
RestSqlQueryOptionsCtrl.templateUrl = 'partials/query.options.html';

export {
  RestSqlDatasource as Datasource,
  RestSqlDatasourceQueryCtrl as QueryCtrl,
  RestSqlConfigCtrl as ConfigCtrl,
  RestSqlQueryOptionsCtrl as QueryOptionsCtrl
};
