import React from "react";
import HeadMain from "@/app/components/HeadMain"; // Import the HeadMain component
import BreadcrumbDashboard from "../components/layouts/BreadcrumbDashboard"; // Import the BreadcrumbDashboard component
import TableMatching from "../components/table/TableMatching"; // Import the TableMatching component

type Props = {};

const Matching = (props: Props) => {
  return (
    <>
      {/* Set the title and meta description of the page */}
      <HeadMain
        title="Matching - Management | Intelligent Resume Matching"
        description="Intelligent Resume Matching"
      />

      {/* Display the breadcrumb */}
      <BreadcrumbDashboard title="Match Candidates With Job Opportunities" />

      {/* Main content of the FAQ page */}
      <div className="px-4 pt-6">
        <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:text-white dark:border-gray-700 sm:p-6 dark:bg-gray-800">
          {/* <div className="font-bold text-lg">Matching Candidate</div> */}

          {/* List of FAQs */}
          <div id="list-faq" className="mt-4">
            <div className="flex flex-col mt-6">
              <div className="overflow-x-auto">
                <div className="inline-block min-w-full align-middle">
                  <div className="overflow-hidden shadow">
                    {/* Render the FAQ table */}
                    <TableMatching />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Matching;
