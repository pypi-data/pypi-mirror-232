import React, { useCallback, useState } from 'react';
import classNames from 'classnames';
import { InputGroup } from '@jupyterlab/ui-components';
import { useDebounce } from 'react-use';

type FilterProps = {
  onFilter?: (value: string) => void;
  placeholder?: string;
  className?: string;
  delay?: number;
};

const blockName = 'jp-hmi-filter';

// also this component could be refactored as a separate hook
// to share debounce logic for each component
// e.g useFilter hook
const Filter: React.FC<FilterProps> = props => {
  const { onFilter, placeholder, className, delay = 100 } = props;
  const [filterValue, setFilterValue] = useState('');

  useDebounce(
    () => {
      if (onFilter) {
        onFilter(filterValue);
      }
    },
    delay,
    [onFilter, filterValue]
  );

  const onFilterChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setFilterValue(event.target.value);
    },
    [setFilterValue]
  );

  return (
    <InputGroup
      value={filterValue}
      onChange={onFilterChange}
      placeholder={placeholder}
      className={classNames(blockName, className)}
    />
  );
};

export default Filter;
