import React from 'react';
import classNames from 'classnames';
import Modal from 'react-modal';

Modal.defaultStyles.overlay.backgroundColor = 'var(--jp-dialog-background)';

type ReturnElementFunction = () => React.ReactElement;

export interface IDialogProps extends Modal.Props {
  title?: string | ReturnElementFunction;
  renderButtons?: ReturnElementFunction;
  fullScreen?: boolean;
}

const blocName = 'jp-hmi-modal';

const Dialog: React.FC<IDialogProps> = props => {
  const {
    title,
    className,
    children,
    renderButtons,
    fullScreen,
    ...otherProps
  } = props;

  const renderTitle = () => {
    if (title) {
      if (typeof title === 'string') {
        return <span className={`${blocName}__title`}>{title}</span>;
      }
      return title();
    }
    return null;
  };

  return (
    <Modal
      ariaHideApp={false}
      className={classNames(`${blocName}__dialog`, className as string, {
        [`${blocName}__dialog_fullscreen`]: fullScreen
      })}
      {...otherProps}
    >
      <div className={`${blocName}__content`}>
        {renderTitle()}
        <div className={`${blocName}__body`}>{children}</div>
        {renderButtons ? (
          <div className={`${blocName}__buttons`}>{renderButtons()}</div>
        ) : null}
      </div>
    </Modal>
  );
};

Dialog.defaultProps = {
  isOpen: true
};

export default Dialog;
