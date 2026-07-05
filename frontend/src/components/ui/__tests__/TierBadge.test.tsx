import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { TierBadge } from "@/components/ui/TierBadge";

describe("TierBadge", () => {
  it("renders the supplied tier", () => {
    render(<TierBadge tier="A" />);

    expect(screen.getByText("A")).toBeInTheDocument();
  });
});
