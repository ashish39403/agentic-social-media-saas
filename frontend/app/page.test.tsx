import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "./page";

describe("HomePage", () => {
  it("identifies the foundation without presenting an unfinished feature", () => {
    render(<HomePage />);
    expect(screen.getByRole("heading", { name: "AI Social Media SaaS" })).toBeInTheDocument();
    expect(screen.getByText(/Product experiences begin/)).toBeInTheDocument();
  });
});
