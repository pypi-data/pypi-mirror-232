import { getAccessToken, getDomain } from '../../utils/settings';

export async function get<T>(url?: string): Promise<T> {
  // eslint-disable-next-line no-undef
  const accessToken = getAccessToken();
  const domain = getDomain();

  if (accessToken && domain) {
    const response = await fetch(`${domain}/api/v1/${url}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`
      }
    });
    const data = await response.json();

    if (response?.status === 200) {
      return data;
    } else {
      throw new Error(data.message);
    }
  } else {
    throw (new Error().message = 'jupyterSettingsError');
  }
}
