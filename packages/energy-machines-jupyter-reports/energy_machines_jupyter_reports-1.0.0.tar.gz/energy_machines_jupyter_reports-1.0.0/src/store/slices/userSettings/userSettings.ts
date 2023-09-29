import { createSlice } from '@reduxjs/toolkit';
import { UserSettings } from '../../../types';

export default createSlice({
  name: 'userSettings',
  initialState: {
    accessToken: '',
    domain: ''
  } as UserSettings,
  reducers: {
    setUserSettings(state, action) {
      state = action.payload;
    },
    setAccessToken(state, action) {
      state.accessToken = action.payload;
    },
    setDomain(state, action) {
      state.domain = action.payload;
    }
  }
});
