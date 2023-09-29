import React from 'react';
import classNames from 'classnames';
import AutoSizer from 'react-virtualized-auto-sizer';
import {
  FixedSizeListProps,
  FixedSizeList as List,
  ListChildComponentProps
} from 'react-window';

type Item = {
  id: string | number;
  name: string;
};

interface IProps
  extends Omit<
    FixedSizeListProps,
    'itemCount' | 'width' | 'height' | 'itemSize' | 'children'
  > {
  isFetchingData: boolean;
  placeholder: string | JSX.Element;
  itemCount?: number;
  itemSize: number;
  items: Item[];
  noRowsText: string;
  selectedItemId: string;
  onSelectedItemChange: (item: Item) => void;
}

const SelectEntityList: React.FC<IProps> = props => {
  const {
    isFetchingData,
    placeholder,
    className,
    items,
    itemSize,
    selectedItemId,
    onSelectedItemChange,
    noRowsText,
    ...listProps
  } = props;

  const Row = (props: ListChildComponentProps): JSX.Element => {
    const { style, data, index } = props;
    const item = data[index];
    return (
      <div
        className={classNames('jp-hmi-select-items-list__item', {
          ['jp-hmi-select-items-list__item_active']: selectedItemId === item.id
        })}
        style={style}
        onClick={(): void => {
          if (selectedItemId !== item.id) {
            onSelectedItemChange(item);
          }
        }}
      >
        {item.name}
      </div>
    );
  };

  return (
    <div className={classNames('jp-hmi-select-items-list', className)}>
      {isFetchingData ? (
        <div className="jp-hmi-select-items-list__placeholder">
          {placeholder}
        </div>
      ) : (
        <AutoSizer className="jp-hmi-select-items-list__auto-sizer-container">
          {({ height, width }) => {
            if (items.length) {
              return (
                <List
                  itemData={items}
                  width={width}
                  height={height}
                  itemCount={items.length}
                  itemSize={itemSize}
                  {...listProps}
                >
                  {Row}
                </List>
              );
            }
            return (
              <div
                style={{ width, height }}
                className="jp-hmi-select-items-list__list_empty"
              >
                {noRowsText}
              </div>
            );
          }}
        </AutoSizer>
      )}
    </div>
  );
};

SelectEntityList.defaultProps = {
  placeholder: '',
  items: [],
  isFetchingData: false,
  noRowsText: 'No items found'
};

export default SelectEntityList;
