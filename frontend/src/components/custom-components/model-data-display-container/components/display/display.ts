/** Each type has its own corresponding properties */
export type DisplayType = "model" | "data";

/** Anything which is displayed must extend this interface */
export interface BaseItemDisplay {
  id: string;
  title: string;
  description: string;
  type: DisplayType;
}