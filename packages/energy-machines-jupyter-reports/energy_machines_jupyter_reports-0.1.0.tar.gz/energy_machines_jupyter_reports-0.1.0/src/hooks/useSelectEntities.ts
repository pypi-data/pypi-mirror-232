import { useCallback, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, SelectionActionsType } from '../store/reducers';
import { SelectionModel } from '../store/slices/selection/helpers';
import IWithId from '../interfaces/IWithId';

type ManageEntity<T> = {
  onSelectAllChange: (prevValue: boolean) => void;
  onSelectEntityChange: (isChecked: boolean, entity: T) => void;
  checkIsChecked: (entity: T) => boolean;
  isAllSelected: boolean;
  selectedEntities: T[];
};

type Args<T> = {
  actions: SelectionActionsType;
  entities: T[];
  getSelectedEntitiesSelector: (state: RootState) => SelectionModel;
  onCheckedEntitiesChange: (entities: T[]) => void;
};

export function useSelectEntities<T extends IWithId>({
  actions,
  entities = [],
  getSelectedEntitiesSelector,
  onCheckedEntitiesChange
}: Args<T>): ManageEntity<T> {
  const dispatch = useDispatch();

  const { isAllSelected, selectedIds, deselectedIds } = useSelector(
    (state: RootState) => {
      return getSelectedEntitiesSelector(state);
    }
  );

  const onSelectAllChange = useCallback(
    prevValue => {
      dispatch(actions.setSelectAll(!prevValue));
    },
    [actions, dispatch]
  );

  const onSelectEntityChange = useCallback(
    (isChecked: boolean, entity: T) => {
      const newSelected = { ...selectedIds };
      const newDeselected = { ...deselectedIds };
      if (isAllSelected) {
        if (isChecked) {
          delete newDeselected[entity.id];
        } else {
          newDeselected[entity.id] = entity.id;
        }
        dispatch(actions.setDeselected(newDeselected));
      } else {
        if (isChecked) {
          newSelected[entity.id] = entity.id;
        } else {
          delete newSelected[entity.id];
        }
        dispatch(actions.setSelected(newSelected));
      }
    },
    [actions, deselectedIds, dispatch, isAllSelected, selectedIds]
  );

  const checkIsChecked = useCallback(
    (entity: T) => {
      if (isAllSelected) {
        return !(entity.id in deselectedIds);
      }
      return entity.id in selectedIds;
    },
    [isAllSelected, selectedIds, deselectedIds]
  );

  const isSelectAllChecked = useMemo(() => {
    if (entities.length) {
      if (isAllSelected) {
        return entities.every(entity => !(entity.id in deselectedIds));
      }
      return entities.reduce((acc, entity) => {
        return acc && entity.id in selectedIds;
      }, true);
    }
    return false;
  }, [selectedIds, isAllSelected, entities, deselectedIds]);

  const selected = useMemo(() => {
    let selectedEntities: T[];
    if (isAllSelected) {
      selectedEntities = entities.filter(
        entity => !(entity.id in deselectedIds)
      );
    } else {
      selectedEntities = entities.filter(entity => entity.id in selectedIds);
    }
    onCheckedEntitiesChange(selectedEntities);
    return selectedEntities;
  }, [
    isAllSelected,
    onCheckedEntitiesChange,
    entities,
    deselectedIds,
    selectedIds
  ]);

  return {
    onSelectAllChange,
    onSelectEntityChange,
    checkIsChecked,
    isAllSelected: isSelectAllChecked,
    selectedEntities: selected
  };
}
