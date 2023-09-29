import React, { useCallback } from 'react';
import { Button } from '@jupyterlab/ui-components';
import { useSelector, useDispatch } from 'react-redux';
import { DateRangePicker, Range } from 'react-date-range';
import endOfDay from 'date-fns/endOfDay';
import { RootState } from '../../../store/reducers';
import { getRanges } from './selectors';
import DateRangeSlice from '../../../store/slices/dateRange';
import Dialog, { IDialogProps } from '../Dialog';

type Props = {
  onDateRangeChange: (range: Range) => void;
} & IDialogProps;

const SetDateRangeDialog: React.FC<Props> = props => {
  const ranges = useSelector((state: RootState) => {
    return getRanges(state);
  });

  const dispatch = useDispatch();

  const { isOpen, onRequestClose, onDateRangeChange } = props;
  const renderButtons = useCallback((): JSX.Element => {
    return (
      <>
        <Button onClick={onRequestClose}>Close</Button>
        <Button
          intent="primary"
          onClick={(): void => {
            const [range] = ranges;
            onDateRangeChange(range);
          }}
        >
          Ok
        </Button>
      </>
    );
  }, [onDateRangeChange, onRequestClose, ranges]);

  const onDateChange = useCallback(
    (item: any): void => {
      dispatch(
        DateRangeSlice.actions.setPeriod({
          startDate: item.range1.startDate.valueOf(),
          endDate: endOfDay(item.range1.endDate).valueOf()
        })
      );
    },
    [dispatch]
  );

  return (
    <Dialog
      isOpen={isOpen}
      title="Select period for report"
      onRequestClose={onRequestClose}
      renderButtons={renderButtons}
    >
      <DateRangePicker
        onChange={onDateChange}
        showPreview={true}
        moveRangeOnFirstSelection={false}
        months={2}
        ranges={ranges}
        direction="horizontal"
      />
      ;
    </Dialog>
  );
};

export default SetDateRangeDialog;
