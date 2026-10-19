import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";

export function TabList({
  active,
  value,
  onChange,
  tabs,
: {
  active?: string;
  value?: string;
  onChange: (value: string) => void;
  tabs: { id?: string; value?: string; label: string }[];
}) {
  const current = active ?? value ?? tabs[0]?.id ?? tabs[0]?.value ?? "";
  return (
    <Tabs value={current} onChange={(_event, next) => onChange(String(next))} sx={{ mb: 2 }} variant="scrollable">
      {tabs.map((tab) => {
        const key = tab.id ?? tab.value ?? tab.label;
        return <Tab key={key} value={key} label={tab.label} />;
      })}
    </Tabs>
  );
}

export { TabList as Tabs };
