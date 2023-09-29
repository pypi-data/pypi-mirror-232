import React from 'react';
import ErrorCode from '../../../enums/ErrorCodes';

export const ErrorMessage: React.FC<any> = props => {
  const { error } = props;
  if (error === ErrorCode.JupyterSettingsError) {
    return (
      <div className="error-message">
        <p className="error-highlight">AccessToken or domain is not defined.</p>
        <p>
          Please go to settings <span>ctrl+,</span> and define the values
        </p>
      </div>
    );
  }
  if (error === ErrorCode.IncorrectCredentials) {
    return (
      <div className="error-message">
        <p className="error-highlight">AccessToken or domain is incorrect.</p>
        <p>
          Please go to settings <span>ctrl+,</span> and correct the values
        </p>
      </div>
    );
  } else {
    return (
      <div className="error-message">
        <p>{error}</p>
      </div>
    );
  }
};
