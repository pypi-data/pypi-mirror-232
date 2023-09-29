import React, { useState, useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import classNames from 'classnames';
import { Button } from '@jupyterlab/ui-components';
import { get, groupBy, find, values } from 'lodash';
import {
  fetchProjectsList,
  fetchTagsListByProjectId
} from '../../../store/actions/entities';
import { makeGetFilteredProjects } from '../../../store/selectors';
import { RootState } from '../../../store/reducers';
import { getTagsListItems } from './selectors';
import Dialog, { IDialogProps } from '../Dialog';
import { Filter } from '../../Filter';
import { SelectProjectsTable, SelectedTagsTable } from '../../Tables';
import { DataToAdd } from '../../../types';
import IProject from '../../../interfaces/IProject';
import { ErrorMessage } from '../ErrorMessage';

type Props = {
  onFinishButtonClick: (data: DataToAdd) => void;
} & IDialogProps;

const blockName = 'jp-hmi-select-tags-from-list';
const buttonClassName = `${blockName}__button`;

enum Step {
  SELECT_PROJECTS,
  SELECT_TAGS
}

const getProjects = makeGetFilteredProjects();

const SelectTagsFromList: React.FC<Props> = props => {
  const { onRequestClose, isOpen, onFinishButtonClick } = props;
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [query, setQuery] = useState('');
  const [step, setStep] = useState(Step.SELECT_PROJECTS);
  const dispatch = useDispatch();

  useEffect(() => {
    if (isOpen) {
      dispatch(fetchProjectsList() as any);
    }
  }, [dispatch, isOpen]);

  const projectsList = useSelector((state: RootState) => {
    return state.projectsList.model;
  });

  const error = useSelector((state: RootState) => {
    return state.projectsList.error;
  });

  const projects = useSelector((state: RootState) => {
    return getProjects(state, query);
  });

  const tags = useSelector((state: RootState) => {
    return getTagsListItems(state, {
      projectsIds: selectedProjects.map(p => p.id),
      query
    });
  });

  const isProjectsFetching = useSelector((state: RootState) => {
    return !state.projectsList.hasBeenFetched;
  });

  const renderTitle = useCallback(() => {
    const title =
      step === Step.SELECT_PROJECTS
        ? 'Select projects from table'
        : 'Select tags from table';
    return (
      <div className={`${blockName}__title-container`}>
        <div className="jp-hmi-modal__title">{title}</div>
        <Filter
          key={step}
          placeholder={
            step === Step.SELECT_PROJECTS
              ? 'Filter projects by name'
              : 'Filter by tag path'
          }
          onFilter={setQuery}
        />
      </div>
    );
  }, [step]);

  const onNextClick = useCallback(() => {
    setStep(Step.SELECT_TAGS);
    setQuery('');
    selectedProjects.forEach(project => {
      dispatch(fetchTagsListByProjectId(project.id) as any);
    });
  }, [dispatch, selectedProjects]);

  const isTagsListFetching = useSelector((state: RootState) => {
    return !selectedProjects.reduce((acc, project) => {
      return (
        acc && get(state, ['tagsList', project.id, 'hasBeenFetched'], false)
      );
    }, true);
  });

  const renderButtons = useCallback((): JSX.Element => {
    if (step === Step.SELECT_PROJECTS) {
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
            intent="primary"
            disabled={!selectedProjects.length}
            onClick={onNextClick}
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
          className={classNames(buttonClassName)}
          intent="primary"
          disabled={isTagsListFetching || !selectedTags.length}
          onClick={(): void => {
            const tagsByProjectId = groupBy(selectedTags, 'projectId');
            const projectsIds = Object.keys(tagsByProjectId);
            const projects: IProject[] = [];
            projectsIds.forEach(projectId => {
              projects.push(find(projectsList, { id: projectId }));
              tagsByProjectId[projectId] = values(
                tagsByProjectId[projectId]
              ).map(tag => tag.path);
            });
            setQuery('');
            setStep(Step.SELECT_PROJECTS);
            onFinishButtonClick({
              tags: tagsByProjectId,
              projects
            });
          }}
        >
          Finish
        </Button>
      </>
    );
  }, [
    isTagsListFetching,
    onFinishButtonClick,
    onNextClick,
    onRequestClose,
    projectsList,
    selectedProjects.length,
    selectedTags,
    step
  ]);

  return (
    <Dialog
      title={renderTitle}
      isOpen={isOpen}
      className={blockName}
      onRequestClose={onRequestClose}
      renderButtons={renderButtons}
    >
      {((): JSX.Element => {
        if (step === Step.SELECT_PROJECTS) {
          if (error) {
            return <ErrorMessage error={error} />;
          }
          return (
            <SelectProjectsTable
              isFetchingData={isProjectsFetching}
              className={`${blockName}__table`}
              projects={projects}
              setSelectedProjects={setSelectedProjects}
            />
          );
        } else {
          return (
            <SelectedTagsTable
              isFetchingData={isTagsListFetching}
              className={`${blockName}__table`}
              tags={tags}
              setSelectedTags={setSelectedTags}
            />
          );
        }
      })()}
    </Dialog>
  );
};

export default SelectTagsFromList;
