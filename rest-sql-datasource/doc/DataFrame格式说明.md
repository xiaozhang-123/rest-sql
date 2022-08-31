##DataFrame格式源码
```typescript
export declare enum FieldType {
    time = "time",
    number = "number",
    string = "string",
    boolean = "boolean",
    other = "other"
}
/**
 * Every property is optional
 *
 * Plugins may extend this with additional properties. Something like series overrides
 */
export interface FieldConfig {
    title?: string;
    filterable?: boolean;
    unit?: string;
    decimals?: number | null;
    min?: number | null;
    max?: number | null;
    mappings?: ValueMapping[];
    thresholds?: ThresholdsConfig;
    color?: FieldColor;
    nullValueMode?: NullValueMode;
    links?: DataLink[];
    noValue?: string;
    custom?: Record<string, any>;
    scopedVars?: ScopedVars;
}
export interface Field<T = any, V = Vector<T>> {
    /**
     * Name of the field (column)
     */
    name: string;
    /**
     *  Field value type (string, number, etc)
     */
    type: FieldType;
    /**
     *  Meta info about how field and how to display it
     */
    config: FieldConfig;
    values: V;
    labels?: Labels;
    /**
     * Cache of reduced values
     */
    calcs?: FieldCalcs;
    /**
     * Convert text to the field value
     */
    parse?: (value: any) => T;
    /**
     * Convert a value for display
     */
    display?: DisplayProcessor;
}
export interface DataFrame extends QueryResultBase {
    name?: string;
    fields: Field[];
    length: number;
}
/**
 * Like a field, but properties are optional and values may be a simple array
 */
export interface FieldDTO<T = any> {
    name: string;
    type?: FieldType;
    config?: FieldConfig;
    values?: Vector<T> | T[];
    labels?: Labels;
}
/**
 * Like a DataFrame, but fields may be a FieldDTO
 */
export interface DataFrameDTO extends QueryResultBase {
    name?: string;
    fields: Array<FieldDTO | Field>;
}
```