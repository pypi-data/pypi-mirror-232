import React, { useCallback, useRef } from 'react';
import { useEffectOnce } from 'react-use';
import { PageTagsData } from './types';

type ResponsePageTagData = {
  tags: Array<PageTagsData>;
  type: string;
};

type Props = {
  onSelectionChanged?(tags: Array<PageTagsData>): void;
  projectId: string;
  pageId: string;
  token: string;
  domain: string;
};

const SelectTagsFromPageView: React.FC<Props> = ({
  pageId,
  projectId,
  token,
  domain,
  onSelectionChanged
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  useEffectOnce(() => {
    window.addEventListener('message', onMessage);
    return (): void => {
      window.removeEventListener('message', onMessage);
    };
  });

  const onMessage = useCallback(
    (e: MessageEvent<string>) => {
      if (typeof e.data === 'string') {
        try {
          const response = JSON.parse(e.data) as ResponsePageTagData;
          if (response.type === 'tagsChanged') {
            if (onSelectionChanged) {
              onSelectionChanged(response.tags);
            }
          }
        } catch (error) {
          //do nothing
        }
      }
    },
    [onSelectionChanged]
  );
  return (
    <div className="jp-hmi-dashboard">
      <iframe
        ref={iframeRef}
        src={`${domain}/shared/${token}/projects/${projectId}/pages/${pageId}`}
      />
    </div>
  );
};

export default SelectTagsFromPageView;
