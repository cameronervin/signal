import { Search } from "lucide-react";

interface Props {
  label: string;
  placeholder: string;
}

export function SearchInput({ label, placeholder }: Props) {
  return (
    <label className="search-input">
      <Search aria-hidden="true" size={15} />
      <span className="sr-only">{label}</span>
      <input placeholder={placeholder} type="search" />
    </label>
  );
}
