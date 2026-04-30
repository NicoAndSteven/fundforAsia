import { useEffect, useRef, useState } from 'react';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { fetchSectors, type SectorItem } from '@/services/market-service';

interface TickerAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

interface Suggestion {
  label: string;
  subtitle: string;
  etfCode: string;
}

export function TickerAutocomplete({
  value,
  onChange,
  placeholder = 'Ticker',
  className,
  disabled,
}: TickerAutocompleteProps) {
  const [sectors, setSectors] = useState<SectorItem[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Load sectors on mount
  useEffect(() => {
    const sectorsFetched = sessionStorage.getItem('sectors_cached');
    if (sectorsFetched) {
      try { setSectors(JSON.parse(sectorsFetched)); } catch {}
    }
    fetchSectors().then(list => {
      setSectors(list);
      try { sessionStorage.setItem('sectors_cached', JSON.stringify(list)); } catch {}
    }).catch(() => {});
  }, []);

  // Filter suggestions based on input
  useEffect(() => {
    if (!value.trim()) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }

    const input = value.trim().toLowerCase();
    if (input.length < 1) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }

    const matches: Suggestion[] = [];

    // Match against sector names, ETF codes, and sector codes
    for (const s of sectors) {
      const name = s.name.toLowerCase();
      const etfCode = s.etf_code;
      const code = s.code.toLowerCase();

      // Prioritize ETF code matches
      if (etfCode && etfCode.includes(input)) {
        matches.push({ label: etfCode, subtitle: s.name, etfCode });
        continue;
      }
      // Sector code matches
      if (code.includes(input)) {
        if (etfCode) matches.push({ label: etfCode, subtitle: s.name, etfCode });
        continue;
      }
      // Chinese name matches (pinyin not supported, only character match)
      if (name.includes(input)) {
        if (etfCode) matches.push({ label: etfCode, subtitle: s.name, etfCode });
        continue;
      }
    }

    // Limit to top 10
    setSuggestions(matches.slice(0, 10));
    setShowDropdown(matches.length > 0);
    setSelectedIndex(-1);
  }, [value, sectors]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSelect = (suggestion: Suggestion) => {
    onChange(suggestion.etfCode);
    setShowDropdown(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showDropdown) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      handleSelect(suggestions[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  return (
    <div className="relative flex-1">
      <Input
        ref={inputRef}
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
        className={cn(className)}
        disabled={disabled}
      />
      {showDropdown && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className={cn(
            "absolute z-50 top-full mt-1 left-0 right-0",
            "max-h-48 overflow-y-auto rounded-md border border-border",
            "bg-popover text-popover-foreground shadow-lg"
          )}
        >
          {suggestions.map((s, i) => (
            <button
              key={`${s.etfCode}-${s.subtitle}`}
              type="button"
              className={cn(
                "flex items-center justify-between w-full px-3 py-2 text-left transition-colors",
                "hover:bg-accent hover:text-accent-foreground",
                i === selectedIndex && "bg-accent text-accent-foreground"
              )}
              onMouseDown={e => {
                e.preventDefault();
                handleSelect(s);
              }}
            >
              <span className="font-mono text-xs font-semibold text-primary">
                {s.label}
              </span>
              <span className="text-xs text-muted-foreground truncate ml-2">
                {s.subtitle}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
