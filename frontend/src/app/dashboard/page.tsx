// Import required components
import HeadMain from "../components/HeadMain"; // Import the HeadMain component
import BreadcrumbDashboard from "./components/layouts/BreadcrumbDashboard"; // Import the BreadcrumbDashboard component

// Define the Dashboard component
export default function Dashboard() {
  return (
    <>
      {/* Set the title and meta description of the page */}
      <HeadMain
        title="Intelligent Resume Matching"
        description="Intelligent Resume Matching"
      />

      {/* Display the breadcrumb */}
      <BreadcrumbDashboard title="Dashboard" />
    </>
  );
}
