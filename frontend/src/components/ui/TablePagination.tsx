import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/Button";

interface Props {
  currentPage: number;
  endIndex: number;
  onPageChange: (page: number) => void;
  pageCount: number;
  startIndex: number;
  totalItems: number;
}

export function TablePagination({ currentPage, endIndex, onPageChange, pageCount, startIndex, totalItems }: Props) {
  if (totalItems === 0) {
    return null;
  }

  return (
    <div className="table-pagination" aria-label="Table pagination">
      <span className="table-pagination-summary">
        Showing {startIndex + 1}-{endIndex} of {totalItems}
      </span>
      <div className="table-pagination-controls">
        <Button
          aria-label="Previous page"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
          size="small"
          variant="secondary"
        >
          <ChevronLeft aria-hidden="true" size={14} />
          Previous
        </Button>
        <span className="table-pagination-page" aria-label={`Page ${currentPage} of ${pageCount}`}>
          Page {currentPage} of {pageCount}
        </span>
        <Button
          aria-label="Next page"
          disabled={currentPage >= pageCount}
          onClick={() => onPageChange(currentPage + 1)}
          size="small"
          variant="secondary"
        >
          Next
          <ChevronRight aria-hidden="true" size={14} />
        </Button>
      </div>
    </div>
  );
}
