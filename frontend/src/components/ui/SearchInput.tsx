import { Search } from "lucide-react";

interface Props {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}

export function SearchInput({ label, placeholder, value, onChange }: Props) {
  return (
    <label className="search-input">
      <Search aria-hidden="true" size={15} />
      <span className="sr-only">{label}</span>
      <input placeholder={placeholder} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
