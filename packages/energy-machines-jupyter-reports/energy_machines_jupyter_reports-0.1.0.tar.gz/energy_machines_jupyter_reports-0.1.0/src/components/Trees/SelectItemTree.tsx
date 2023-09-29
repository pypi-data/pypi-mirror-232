import React, { FC, useCallback, useRef, useEffect } from 'react';
import classNames from 'classnames';
import { FixedSizeTree as Tree } from 'react-vtree';
import AutoSizer from 'react-virtualized-auto-sizer';
import folderOpenned from '../../icons/folderOpenned';
import folder from '../../icons/folder';
import page from '../../icons/page';
import PageType from '../../enums/PageType';

// Most of this code just a copypaste from docs

const blockName = 'select-item-tree';

// Node component receives all the data we created in the `treeWalker` +
// internal openness state (`isOpen`), function to change internal openness
// state (`toggle`) and `style` parameter that should be added to the root div.
const Node: FC<any> = ({
  data: { isLeaf, path, nestingLevel, id, selected, onSelectedItemChange },
  isOpen,
  style,
  toggle
}) => (
  <div
    style={{
      ...style,
      marginLeft: nestingLevel * 30
    }}
    className={classNames(`${blockName}__item`, {
      [`${blockName}__item_folder`]: !isLeaf,
      [`${blockName}__item_selected`]: selected
    })}
    onClick={
      !isLeaf
        ? toggle
        : (): void => {
            onSelectedItemChange(id);
          }
    }
  >
    {!isLeaf ? (
      <div
        className={classNames(`${blockName}__arrow`, {
          [`${blockName}__arrow_expanded`]: isOpen
        })}
      />
    ) : null}
    {!isLeaf &&
      (isOpen ? (
        <folderOpenned.react className={`${blockName}__folder-icon`} />
      ) : (
        <folder.react className={`${blockName}__folder-icon`} />
      ))}
    <div className={`${blockName}__item-info`}>
      {isLeaf ? <page.react className={`${blockName}__item-icon`} /> : null}
      <span>{path}</span>
    </div>
  </div>
);

const SelectItemTree = (props: any): JSX.Element => {
  const {
    isFetchingData,
    className,
    placeholderText,
    tree,
    itemSize,
    selectedItemId,
    noDataText,
    expandItems,
    onSelectedItemChange
  } = props;

  const treeRef = useRef(null);

  useEffect(() => {
    treeRef.current?.recomputeTree({
      useDefaultOpenness: true
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [treeRef.current]);

  const treeWalker = useCallback(
    function*(refresh): any {
      const stack = [];
      for (let i = tree.length - 1; i >= 0; i--) {
        stack.push({
          nestingLevel: 0,
          node: tree[i]
        });
      }

      while (stack.length !== 0) {
        const {
          node: { children = [], id, name, type },
          nestingLevel
        } = stack.pop();

        const isOpened = yield refresh || expandItems
          ? {
              id,
              isLeaf: type === PageType.Page,
              isOpenByDefault: expandItems,
              selected: selectedItemId === id,
              name,
              path: name,
              nestingLevel,
              onSelectedItemChange
            }
          : id;

        if (children.length !== 0 && isOpened) {
          for (let i = children.length - 1; i >= 0; i--) {
            stack.push({
              nestingLevel: nestingLevel + 1,
              node: children[i]
            });
          }
        }
      }
    },
    [tree, selectedItemId, onSelectedItemChange, expandItems]
  );

  return (
    <div className={classNames(blockName, className)}>
      <AutoSizer className={`${blockName}__autosizer`}>
        {({ width, height }): React.ReactElement => {
          if (isFetchingData) {
            return (
              <div
                style={{ width, height }}
                className={`${blockName}__placeholder`}
              >
                {placeholderText}
              </div>
            );
          }
          if (!tree.length) {
            return (
              <div
                style={{ width, height }}
                className={`${blockName}__placeholder`}
              >
                {noDataText}
              </div>
            );
          }
          return (
            <Tree
              ref={treeRef}
              treeWalker={treeWalker}
              itemSize={itemSize}
              height={height}
              width={width}
            >
              {Node}
            </Tree>
          );
        }}
      </AutoSizer>
    </div>
  );
};

export default SelectItemTree;
