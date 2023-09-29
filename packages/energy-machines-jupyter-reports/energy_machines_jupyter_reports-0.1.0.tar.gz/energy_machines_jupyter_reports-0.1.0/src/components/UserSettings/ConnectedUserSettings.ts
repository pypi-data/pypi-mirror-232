import React from 'react';
import { useDispatch } from 'react-redux';
import { useEffect } from 'react';
import userSettingsSlice from '../../store/slices/userSettings/userSettings';
import { UserSettings } from '../../types';
import { setAccessToken, setDomain } from '../../utils/settings';

const ConnectedUserSettings: React.FC<{
  children: any;
  userSettings: UserSettings;
}> = ({ userSettings, children }) => {
  const dispatch = useDispatch();
  let accessToken: string | null = null;
  let domain: string | null = null;
  if (userSettings) {
    accessToken = userSettings.accessToken;
  }
  if (userSettings) {
    domain = userSettings.domain;
  }

  useEffect(() => {
    if (accessToken !== null) {
      setAccessToken(accessToken);
      dispatch(userSettingsSlice.actions.setAccessToken(accessToken));
    }

    if (domain !== null) {
      setDomain(domain);
      dispatch(userSettingsSlice.actions.setDomain(domain));
    }
  }, [dispatch, accessToken, domain]);

  return children;
};

export default ConnectedUserSettings;
