import { createSelector } from 'reselect';
import { Range } from 'react-date-range';
import { RootState } from '../../../../store/reducers';
import { DateRange } from '../../../../store/slices/dateRange';

export const getRanges = createSelector<RootState, DateRange, Range[]>(
  state => state.dateRange,
  range => {
    return [
      {
        startDate: new Date(range.startDate),
        endDate: new Date(range.endDate)
      }
    ];
  }
);
