import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { Range } from 'react-date-range';
import store from '../../store';
import {
  SelectTagsFromListDialog,
  SetDateRangeDialog,
  SelectTagsFromPageDialog
} from '../dialogs';
import ConnectedUserSettings from '../UserSettings';
import { DataToAdd, UserSettings } from '../../types';

type Props = {
  isSelectTagsFromListDialogOpen: boolean;
  isSelectTagsFromPageDialogOpen: boolean;
  isSetPeriodDialogOpen: boolean;
  userSettings: UserSettings;
  onDataAdded?: () => DataToAdd;
  onCloseSelectTagsFromListDialog: () => void;
  onCloseSetPeriodDialog: () => void;
  onFinishButtonClick: (data: DataToAdd) => void;
  onDateRangeChange: (range: Range) => void;
  onSelectTagsFromPageDialog?: () => void;
  onCloseSelectTagsFromPageDialog: () => void;
};

const App: React.FC<Props> = props => {
  const {
    userSettings,
    onCloseSelectTagsFromListDialog,
    onFinishButtonClick,
    isSelectTagsFromListDialogOpen,
    isSetPeriodDialogOpen,
    isSelectTagsFromPageDialogOpen,
    onCloseSetPeriodDialog,
    onDateRangeChange,
    onCloseSelectTagsFromPageDialog
  } = props;

  return ReactDOM.createPortal(
    <Provider store={store}>
      <ConnectedUserSettings userSettings={userSettings}>
        <SelectTagsFromListDialog
          isOpen={isSelectTagsFromListDialogOpen}
          onRequestClose={onCloseSelectTagsFromListDialog}
          onFinishButtonClick={onFinishButtonClick}
        />
        <SetDateRangeDialog
          isOpen={isSetPeriodDialogOpen}
          onRequestClose={onCloseSetPeriodDialog}
          onDateRangeChange={onDateRangeChange}
        />
        <SelectTagsFromPageDialog
          isOpen={isSelectTagsFromPageDialogOpen}
          onRequestClose={onCloseSelectTagsFromPageDialog}
          onFinish={onFinishButtonClick}
        />
      </ConnectedUserSettings>
    </Provider>,
    document.body
  );
};

App.defaultProps = {
  isSelectTagsFromListDialogOpen: false,
  isSelectTagsFromPageDialogOpen: false,
  isSetPeriodDialogOpen: false
};

export default App;
