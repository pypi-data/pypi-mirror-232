export const DOMAIN = 'https://www.energymachines.cloud';
export const SETTINGS_PREFIX = 'energy_machines_jupyter_reports';

const accessTokenPrefix = `${SETTINGS_PREFIX}_accessToken`;
const domainPrefix = `${SETTINGS_PREFIX}_domain`;
export const setAccessToken = (token: string): void =>
  localStorage.setItem(accessTokenPrefix, token);
export const getAccessToken = () => localStorage.getItem(accessTokenPrefix);
export const getDomain = () => localStorage.getItem(domainPrefix);
export const setDomain = (domain: string): void =>
  localStorage.setItem(domainPrefix, domain);
