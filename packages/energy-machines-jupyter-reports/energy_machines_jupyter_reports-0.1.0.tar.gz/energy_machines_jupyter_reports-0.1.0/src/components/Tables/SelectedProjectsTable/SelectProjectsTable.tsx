import React, { useMemo, useCallback } from 'react';
import { Column } from 'react-virtualized';
import SelectItemsTable from '../SelectItemsTable';
import IProject from '../../../interfaces/IProject';
import { useSelectEntities } from '../../../hooks';
import { selectedProjectsSlice } from '../../../store/slices/selection';

type Props = {
  projects: IProject[];
  className?: string;
  setSelectedProjects: (selectedProjects: IProject[]) => void;
  isFetchingData: boolean;
};

const SelectProjectsTable: React.FC<Props> = props => {
  const { className, projects, setSelectedProjects, isFetchingData } = props;

  const {
    onSelectAllChange,
    onSelectEntityChange,
    checkIsChecked,
    isAllSelected,
    selectedEntities: selectedProjects
  } = useSelectEntities({
    entities: projects || [],
    actions: selectedProjectsSlice.actions,
    getSelectedEntitiesSelector: state => state.selectedProjects,
    onCheckedEntitiesChange: setSelectedProjects
  });

  const selectItemsText = useMemo(() => {
    return `${selectedProjects.length} projects selected`;
  }, [selectedProjects]);

  const rowGetter = useCallback(
    ({ index }) => {
      return projects[index];
    },
    [projects]
  );

  return (
    <SelectItemsTable
      className={className}
      numberOfSelectedItems={selectedProjects.length}
      allItemsSelectedText="All projects selected"
      noItemsSelectedText="No projects selected"
      placeholder="Fetching projects..."
      noDataText="No projects found"
      selectedItemsText={selectItemsText}
      isItemChecked={checkIsChecked}
      onItemChange={onSelectEntityChange}
      onSelectAllChange={onSelectAllChange}
      isSelectAllChecked={isAllSelected}
      isFetchingData={isFetchingData}
      rowHeight={34}
      rowCount={projects.length}
      rowGetter={rowGetter}
      headerHeight={40}
      height={300}
      width={300}
    >
      <Column
        label="Project name"
        dataKey="name"
        flexGrow={1}
        flexShrink={0}
        width={1}
      />
    </SelectItemsTable>
  );
};

export default SelectProjectsTable;
