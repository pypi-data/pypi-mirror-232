import { ReactNode } from "react";

export type PillProps = {
  children: ReactNode;
  color?: string;
};

export const Pill = ({ children }: PillProps) => {
  return (
    <span className="rounded-full align-middle px-2 py-1 text-white ml-1 overflow-ellipsis overflow-hidden h-8 w-24 max-w-xl bg-blue-500 inline-block whitespace-nowrap">
      {children}
    </span>
  );
};
