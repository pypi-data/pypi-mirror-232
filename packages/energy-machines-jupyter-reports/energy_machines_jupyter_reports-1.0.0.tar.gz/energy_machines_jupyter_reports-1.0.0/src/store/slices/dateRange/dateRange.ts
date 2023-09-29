import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type DateRange = {
  startDate: number;
  endDate: number;
};

const now = Date.now();

const initialState = {
  startDate: now,
  endDate: now
} as DateRange;

export default createSlice({
  name: 'dateRange',
  initialState,
  reducers: {
    setPeriod: (state, action: PayloadAction<DateRange>): void => {
      state.startDate = action.payload.startDate;
      state.endDate = action.payload.endDate;
    }
  }
});
