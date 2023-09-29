import { FixedSizeNodeData } from 'react-vtree';

export type TreeWalker<
  TData extends FixedSizeNodeData,
  TMeta = {}
> = () => Generator<
  TreeWalkerValue<TData, TMeta> | undefined,
  undefined,
  TreeWalkerValue<TData, TMeta>
>;

export type TreeWalkerValue<
  TData extends FixedSizeNodeData,
  TMeta = {}
> = Readonly<{ data: TData } & TMeta>;
