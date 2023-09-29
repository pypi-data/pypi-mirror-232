import React, { useCallback, useEffect, useState } from 'react';
import { get } from 'lodash';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../../store/reducers';
import { fetchPagesTree } from '../../../store/actions/entities';
import { getFilteredPages } from '../../../store/selectors';
import { SelectItemTree } from '../../Trees';

type Props = {
  onSelectedPageChange: (id: string) => void;
  projectId: string;
  query?: string;
};

const SelectPage: React.FC<Props> = props => {
  const { projectId, onSelectedPageChange, query } = props;

  const dispatch = useDispatch();
  const [selectedPageId, setSelectedPageId] = useState();

  const pagesTree = useSelector((state: RootState) => {
    return getFilteredPages(state, { projectId, query });
  });

  const isPagesFetching = useSelector((state: RootState) => {
    return !get(state, ['pagesTree', projectId, 'hasBeenFetched'], false);
  });

  useEffect(() => {
    dispatch(fetchPagesTree(projectId) as any);
  }, [projectId, dispatch]);

  useEffect(() => {
    onSelectedPageChange(selectedPageId);
  }, [onSelectedPageChange, selectedPageId]);

  const onChange = useCallback(pageId => {
    setSelectedPageId(pageId);
  }, []);

  return (
    <SelectItemTree
      itemSize={40}
      isFetchingData={isPagesFetching}
      placeholderText="Fetching pages"
      noDataText="No pages found"
      selectedItemId={selectedPageId}
      tree={get(pagesTree, 'children', [])}
      onSelectedItemChange={onChange}
      expandItems={!!query}
    />
  );
};

export default SelectPage;
