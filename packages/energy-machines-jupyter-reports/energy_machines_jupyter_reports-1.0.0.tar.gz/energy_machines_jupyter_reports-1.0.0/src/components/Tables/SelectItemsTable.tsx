import React, { useMemo, useCallback } from 'react';
import classNames from 'classnames';
import { Table, Column, TableProps, AutoSizer } from 'react-virtualized';
import { Checkbox } from '@jupyterlab/ui-components';

export type SelectItemsTableProps = {
  className?: string;
  isSelectAllChecked?: boolean;
  numberOfSelectedItems: number;
  allItemsSelectedText: string;
  noItemsSelectedText: string;
  selectedItemsText: string;
  noDataText?: string;
  isItemChecked: (item: any) => boolean;
  onItemChange: (isChecked: boolean, item: any) => void;
  onSelectAllChange: (prevSelected: boolean) => void;
  isFetchingData?: boolean;
  placeholder?: string;
} & TableProps;

const blockName = 'jp-hmi-table';

const SelectItemsTable: React.FC<SelectItemsTableProps> = props => {
  const {
    className,
    isSelectAllChecked,
    numberOfSelectedItems,
    allItemsSelectedText,
    noItemsSelectedText,
    selectedItemsText,
    children,
    rowClassName,
    onItemChange,
    isItemChecked,
    onSelectAllChange,
    noDataText,
    isFetchingData,
    placeholder,
    ...tableProps
  } = props;

  const renderSelectedBlock = useMemo(() => {
    if (isFetchingData) {
      return null;
    }
    let text;
    if (numberOfSelectedItems) {
      if (isSelectAllChecked) {
        text = allItemsSelectedText;
      } else {
        text = selectedItemsText;
      }
    } else {
      text = noItemsSelectedText;
    }
    return (
      <div
        className={classNames(`${blockName}__selected-container`, {
          [`${blockName}__selected-container_with-selected-items`]:
            isSelectAllChecked || !!numberOfSelectedItems
        })}
      >
        {text}
      </div>
    );
  }, [
    allItemsSelectedText,
    isSelectAllChecked,
    noItemsSelectedText,
    numberOfSelectedItems,
    selectedItemsText,
    isFetchingData
  ]);

  const renderCheckAllHeaderRow = useCallback(() => {
    return (
      <Checkbox
        className={`${blockName}__checkbox`}
        checked={isSelectAllChecked}
        onChange={(): void => onSelectAllChange(isSelectAllChecked)}
      />
    );
  }, [isSelectAllChecked, onSelectAllChange]);

  const noRowsRenderer = useCallback(() => {
    return <div className={`${blockName}__no-data-text`}>{noDataText}</div>;
  }, [noDataText]);

  const renderCell = useCallback(
    item => {
      return (
        <Checkbox
          className={`${blockName}__checkbox`}
          checked={isItemChecked(item.rowData)}
          onChange={(e: React.ChangeEvent<HTMLInputElement>): void => {
            onItemChange(e.target.checked, item.rowData);
          }}
        />
      );
    },
    [isItemChecked, onItemChange]
  );

  return (
    <div className={classNames(blockName, className)}>
      {!isFetchingData ? (
        renderSelectedBlock
      ) : (
        <div className={`${blockName}__placeholder`}>{placeholder}</div>
      )}
      {!isFetchingData ? (
        <div className={`${blockName}__auto-sizer`}>
          <AutoSizer>
            {({ width, height }) => (
              <Table
                className={`${blockName}__table`}
                {...tableProps}
                noRowsRenderer={noRowsRenderer}
                width={width}
                height={height}
                rowClassName={classNames(
                  `${blockName}__row`,
                  rowClassName as string
                )}
              >
                <Column
                  width={26}
                  dataKey="id"
                  headerRenderer={renderCheckAllHeaderRow}
                  cellRenderer={renderCell}
                />
                {children}
              </Table>
            )}
          </AutoSizer>
        </div>
      ) : null}
    </div>
  );
};

export default SelectItemsTable;
