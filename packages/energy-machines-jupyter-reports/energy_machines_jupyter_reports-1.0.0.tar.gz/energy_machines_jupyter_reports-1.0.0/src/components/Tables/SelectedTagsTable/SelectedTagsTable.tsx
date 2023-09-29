import React, { useCallback, useMemo } from 'react';
import { useSelectEntities } from '../../../hooks';
import { Column } from 'react-virtualized';
import { selectedTagsSlice } from '../../../store/slices/selection';
import SelectItemsTable from '../SelectItemsTable';
import { ITagTableItem } from '../../dialogs/SelectTagsFromList/selectors';

type Props = {
  tags: ITagTableItem[];
  className: string;
  setSelectedTags: (selectedProjects: ITagTableItem[]) => void;
  isFetchingData: boolean;
};

const blockName = 'jp-hmi-select-tags-table';

const SelectedTagsTable: React.FC<Props> = props => {
  const { tags, setSelectedTags, className } = props;
  const {
    onSelectAllChange,
    onSelectEntityChange,
    checkIsChecked,
    isAllSelected,
    selectedEntities: selectedTags
  } = useSelectEntities<ITagTableItem>({
    entities: tags || [],
    actions: selectedTagsSlice.actions,
    getSelectedEntitiesSelector: state => state.selectedTags,
    onCheckedEntitiesChange: setSelectedTags
  });

  const selectItemsText = useMemo(() => {
    return `${selectedTags.length} tags selected`;
  }, [selectedTags]);

  const rowGetter = useCallback(
    ({ index }) => {
      return tags[index];
    },
    [tags]
  );

  return (
    <SelectItemsTable
      className={className}
      numberOfSelectedItems={selectedTags.length}
      allItemsSelectedText="All tags selected"
      noItemsSelectedText="No tags selected"
      noDataText="No tags found"
      placeholder="Fetching tags"
      selectedItemsText={selectItemsText}
      isItemChecked={checkIsChecked}
      onItemChange={onSelectEntityChange}
      onSelectAllChange={onSelectAllChange}
      isSelectAllChecked={isAllSelected}
      rowHeight={34}
      rowCount={tags.length}
      rowGetter={rowGetter}
      headerHeight={40}
      height={300}
      width={300}
    >
      <Column
        className={`${blockName}__cell`}
        label="Tag name"
        dataKey="name"
        width={1}
        flexGrow={1}
      />
      <Column
        className={`${blockName}__cell ${blockName}__cell_location`}
        label="Location"
        dataKey="path"
        width={1}
        flexGrow={2}
      />
      <Column
        className={`${blockName}__cell ${blockName}__cell_project-name`}
        label="Project name"
        dataKey="projectName"
        width={100}
        flexShrink={0}
      />
    </SelectItemsTable>
  );
};

export default SelectedTagsTable;
