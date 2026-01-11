<script setup lang="ts">
import SignupModal from "@/components/SignupForm/SignupModal.vue";
import { getCSRFToken } from "@/utils/csrf";
import { useRouter } from "vue-router";
import { ref } from "vue";
import { toast } from "vue-sonner";
import type { DateValue } from "@internationalized/date";

const user = ref<any>();
const router = useRouter();

type UserSignup = {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  date_of_birth: DateValue;
};

const signup = async (signupDetails: UserSignup): Promise<any> => {
  const csrfToken = getCSRFToken();

  if (!csrfToken) {
    throw Error("No CSRF Token - make sure cookies are enabled");
  }

  // Convert DateValue to YYYY-MM-DD format
  const dateOfBirth = `${signupDetails.date_of_birth.year}-${String(
    signupDetails.date_of_birth.month
  ).padStart(2, "0")}-${String(signupDetails.date_of_birth.day).padStart(
    2,
    "0"
  )}`;

  const response = await fetch("http://localhost:8000/signup/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    credentials: "include", // Important: sends cookies
    body: JSON.stringify({
      first_name: signupDetails.first_name,
      last_name: signupDetails.last_name,
      email: signupDetails.email,
      password: signupDetails.password,
      date_of_birth: dateOfBirth,
    }),
  });

  return response.json();
};

const handleSignup = async (signupDetails: UserSignup) => {
  try {
    const result = await signup(signupDetails);

    if (result.error) {
      openErrorPopup(result.error);
    } else if (result.success) {
      user.value = result.user;
      toast("Success", {
        description: "Account created successfully! Redirecting...",
      });
      // Redirect to main page or dashboard after successful signup
      setTimeout(() => {
        router.push("/");
      }, 1500);
    }
    console.log("Signup result:", result);
  } catch (err) {
    console.error("Error while signing up:", err);
    openErrorPopup("An error occurred while creating your account");
  }
};

const openErrorPopup = (errorMessage: string) => {
  toast("Error", {
    description: errorMessage,
    action: {
      label: "Close",
      onClick: () => console.log("close"),
    },
  });
};
</script>

<template>
  <div class="min-w-lvw min-h-lvh flex items-center justify-center">
    <SignupModal
      @signupPressed="
        (signupDetails) => {
          handleSignup(signupDetails);
        }
      "
    />
  </div>
</template>
