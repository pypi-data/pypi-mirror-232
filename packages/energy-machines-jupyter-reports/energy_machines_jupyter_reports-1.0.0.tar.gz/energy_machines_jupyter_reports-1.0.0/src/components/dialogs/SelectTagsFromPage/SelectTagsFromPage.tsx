import React, { useCallback, useEffect, useState } from 'react';
import classNames from 'classnames';
import { useDispatch, useSelector } from 'react-redux';
import { Button } from '@jupyterlab/ui-components';
import { find, get } from 'lodash';
import { fetchProjectsList } from '../../../store/actions/entities';
import {
  selectedPagesSlice,
  selectedProjectsSlice
} from '../../../store/slices/selection';
import { RootState } from '../../../store/reducers';
import { makeGetFilteredProjects } from '../../../store/selectors';
import Dialog, { IDialogProps } from '../Dialog';
import { SelectEntityList } from '../../Lists';
import { Filter } from '../../Filter';
import { SelectPageFromTree } from '../../Trees';
import SelectTagsFromPageView from '../../pages/SelectTagsFromPageView';
import { PageTagsData } from '../../pages/types';
import { DataToAdd } from '../../../types';
import IProject from '../../../interfaces/IProject';
import { groupBy, values } from 'lodash';
import { ErrorMessage } from '../ErrorMessage';

enum Step {
  SELECT_PROJECT,
  SELECT_PAGE,
  SELECT_TAGS
}

const getProjects = makeGetFilteredProjects();

const blockName = 'jp-hmi-select-tags-from-page';
const buttonClassName = 'jp-hmi-select-tags-from-page__button';

const TitleView: React.FC<{ children: any }> = ({ children }) => {
  return <div className={`${blockName}__title-container`}>{children}</div>;
};

type Props = {
  onFinish: (data: DataToAdd) => void;
} & IDialogProps;

const SelectTagsFromPage: React.FC<Props> = props => {
  const { onRequestClose, isOpen, onFinish } = props;
  const dispatch = useDispatch();
  const [query, setQuery] = useState('');
  const [step, setStep] = useState(Step.SELECT_PROJECT);
  const [selectedTags, setSelectedTags] = useState([]);

  const setSelectedProjectId = useCallback(
    projectId => {
      dispatch(
        selectedProjectsSlice.actions.setSelected(
          projectId ? { [projectId]: projectId } : {}
        )
      );
    },
    [dispatch]
  );

  const setSelectedPageId = useCallback(
    pageId => {
      dispatch(selectedPagesSlice.actions.setSelected(pageId ? [pageId] : []));
    },
    [dispatch]
  );
  const selectedProjectId = useSelector((state: RootState) => {
    return Object.values(state.selectedProjects.selectedIds)[0];
  });
  const selectedPageId = useSelector((state: RootState) => {
    return Object.values(state.selectedPages.selectedIds)[0];
  });

  const filteredProjects = useSelector((state: RootState) => {
    return getProjects(state, query);
  });

  const projects = useSelector((state: RootState) => {
    return getProjects(state, '');
  });
  const token = useSelector((state: RootState) => {
    return state.userSettings.accessToken;
  });

  const error = useSelector((state: RootState) => {
    return state.projectsList.error;
  });

  const domain = useSelector((state: RootState) => {
    return state.userSettings.domain;
  });

  useEffect(() => {
    if (isOpen && step === Step.SELECT_PROJECT) {
      dispatch(fetchProjectsList() as any);
    }
  }, [dispatch, isOpen, step]);

  useEffect(() => {
    if (
      isOpen &&
      step === Step.SELECT_PROJECT &&
      !filteredProjects.find(
        (project: IProject) => project.id === selectedProjectId
      )
    ) {
      if (filteredProjects && filteredProjects.length) {
        setSelectedProjectId(filteredProjects[0].id);
      } else if (filteredProjects && !filteredProjects.length) {
        setSelectedProjectId(undefined);
      }
    }
  }, [
    filteredProjects,
    query,
    selectedProjectId,
    setSelectedProjectId,
    step,
    isOpen
  ]);

  const isProjectsFetching = useSelector((state: RootState) => {
    return !state.projectsList.hasBeenFetched;
  });
  const projectsList = useSelector((state: RootState) => {
    return state.projectsList.model;
  });

  const renderTitle = (): JSX.Element => {
    if (step === Step.SELECT_PROJECT) {
      return (
        <TitleView>
          <>
            <div className="jp-hmi-modal__title">Select project from list</div>
            <Filter
              key={step}
              placeholder="Filter by project name"
              onFilter={setQuery}
            />
          </>
        </TitleView>
      );
    } else if (step === Step.SELECT_PAGE) {
      const activeProject =
        find(projects || [], {
          id: selectedProjectId
        }) || null;

      return (
        <TitleView>
          <>
            <div className="jp-hmi-modal__title">
              Select page on {get(activeProject, 'name', '')}
            </div>
            <Filter
              key={step}
              placeholder="Filter by page path"
              onFilter={setQuery}
            />
          </>
        </TitleView>
      );
    } else if (step === Step.SELECT_TAGS) {
      return <div className="jp-hmi-modal__title">Select tags on page</div>;
    }
    return null;
  };

  const onNextButtonClick = (): void => {
    if (step === Step.SELECT_PROJECT) {
      setStep(Step.SELECT_PAGE);
    }
    if (step === Step.SELECT_PAGE) {
      setStep(Step.SELECT_TAGS);
    }
    setQuery('');
  };

  const onPrevButtonClick = (): void => {
    if (step === Step.SELECT_PAGE) {
      setStep(Step.SELECT_PROJECT);
    }
    if (step === Step.SELECT_TAGS) {
      setStep(Step.SELECT_PAGE);
    }
    setQuery('');
  };

  const onFinishButtonClick = (e: React.MouseEvent): void => {
    const tagsByProjectId = groupBy(selectedTags, 'projectId');
    const projectsIds = Object.keys(tagsByProjectId);
    const projects: IProject[] = [];
    projectsIds.forEach(projectId => {
      projects.push(find(projectsList, { id: projectId }));
      tagsByProjectId[projectId] = values(tagsByProjectId[projectId]).map(
        tag => tag.path
      );
    });
    onFinish({
      projects,
      tags: tagsByProjectId
    });
    onRequestClose(e);
  };

  const renderButtons = (): JSX.Element => {
    if (step === Step.SELECT_TAGS) {
      return (
        <>
          <Button
            className={classNames(buttonClassName, `${buttonClassName}_cancel`)}
            onClick={onRequestClose}
          >
            Cancel
          </Button>
          <Button
            className={classNames(buttonClassName, `${buttonClassName}_prev`)}
            intent="primary"
            onClick={onPrevButtonClick}
          >
            Prev
          </Button>
          <Button
            className={classNames(buttonClassName, `${buttonClassName}_next`)}
            intent="primary"
            onClick={onFinishButtonClick}
          >
            Finish
          </Button>
        </>
      );
    }
    if (step === Step.SELECT_PROJECT) {
      return (
        <>
          <Button
            className={classNames(buttonClassName, `${buttonClassName}_cancel`)}
            onClick={onRequestClose}
          >
            Cancel
          </Button>
          <Button
            className={classNames(buttonClassName, `${buttonClassName}_next`)}
            intent="primary"
            disabled={!selectedProjectId}
            onClick={onNextButtonClick}
          >
            Next
          </Button>
        </>
      );
    }
    return (
      <>
        <Button
          className={classNames(buttonClassName, `${buttonClassName}_cancel`)}
          onClick={onRequestClose}
        >
          Cancel
        </Button>
        <Button
          className={classNames(buttonClassName, `${buttonClassName}_cancel`)}
          onClick={onPrevButtonClick}
        >
          Select project
        </Button>
        <Button
          className={classNames(buttonClassName, `${buttonClassName}_next`)}
          intent="primary"
          disabled={!selectedPageId}
          onClick={onNextButtonClick}
        >
          Next
        </Button>
      </>
    );
  };

  const onSelectItemsChange = useCallback(
    project => {
      setSelectedProjectId(project.id);
    },
    [setSelectedProjectId]
  );

  const onSelectedPageChange = useCallback(
    pageId => {
      setSelectedPageId(pageId);
    },
    [setSelectedPageId]
  );

  const onTagsChanged = (data: PageTagsData[]): void => {
    setSelectedTags(data);
  };

  return (
    <Dialog
      title={renderTitle}
      isOpen={isOpen}
      renderButtons={renderButtons}
      fullScreen={step === Step.SELECT_TAGS}
    >
      {((): JSX.Element => {
        if (error) {
          return <ErrorMessage error={error} />;
        }
        if (step === Step.SELECT_PROJECT) {
          return (
            <SelectEntityList
              itemSize={40}
              isFetchingData={isProjectsFetching}
              items={filteredProjects}
              selectedItemId={selectedProjectId}
              placeholder="Fetching projects..."
              noRowsText="No projects found"
              onSelectedItemChange={onSelectItemsChange}
            />
          );
        } else if (step === Step.SELECT_PAGE) {
          return (
            <SelectPageFromTree
              projectId={selectedProjectId}
              onSelectedPageChange={onSelectedPageChange}
              query={query}
            />
          );
        } else if (step === Step.SELECT_TAGS) {
          return (
            <SelectTagsFromPageView
              onSelectionChanged={onTagsChanged}
              pageId={selectedPageId}
              projectId={selectedProjectId}
              token={token}
              domain={domain}
            />
          );
        }
        return null;
      })()}
    </Dialog>
  );
};

export default SelectTagsFromPage;
