import ProtectedRoute from "@/components/custom-components/auth/protected-route/protected-route";
import HomePage from "./home-page";
import SubLayout from "./sub-layout";

export default function Home() {
  return (
    <ProtectedRoute>
        <SubLayout>
          <HomePage />
        </SubLayout>
    </ProtectedRoute>

  );
}
