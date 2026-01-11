<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import { useRouter } from "vue-router";
import * as z from "zod";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { FieldDescription } from "@/components/ui/field";
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import DatePicker from "../DatePicker/DatePicker.vue";
import type { DateValue } from "@internationalized/date";

const router = useRouter();

type UserSignup = {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  date_of_birth: DateValue;
};

const emit = defineEmits<{
  (e: "signupPressed", details: UserSignup): void;
}>();

const signupValidationSchema = toTypedSchema(
  z.object({
    first_name: z.string().min(1, { message: "First Name is required" }),
    last_name: z.string().min(1, { message: "Last Name is required" }),
    email: z
      .string()
      .min(1, { message: "Email is required" })
      .email("Invalid Email Address"),
    password: z
      .string()
      .min(8, { message: "Password must be 8 characters long" }),
    date_of_birth: z.any(), // Need to figure out how to properly validate the datetime although with the datepicker it's not exactly needed
  }),
);

const signupForm = useForm({
  validationSchema: signupValidationSchema,
});

const onSubmit = signupForm.handleSubmit((values) => {
  const signupDetails = {
    first_name: values.first_name,
    last_name: values.last_name,
    email: values.email,
    password: values.password,
    date_of_birth: values.date_of_birth,
  };
  emit("signupPressed", signupDetails);
});

const navigateToLogin = () => {
  router.push("/login");
};

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <div :class="cn('flex flex-col gap-6', props.class)">
    <Card>
      <CardHeader class="text-center">
        <CardTitle class="text-xl"> Create your account </CardTitle>
        <CardDescription>
          Enter your email below to create your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit="onSubmit">
          <FormField v-slot="{ componentField }" name="first_name">
            <FormItem class="mb-2">
              <FormLabel>First Name</FormLabel>
              <FormControl>
                <Input
                  type="text"
                  placeholder="Enter your first name"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
          <FormField v-slot="{ componentField }" name="last_name">
            <FormItem class="mb-2">
              <FormLabel>Last Name</FormLabel>
              <FormControl>
                <Input
                  type="text"
                  placeholder="Enter your last name"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
          <FormField v-slot="{ componentField }" name="email">
            <FormItem class="mb-2">
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="text"
                  placeholder="Enter your email"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
          <FormField v-slot="{ componentField }" name="password">
            <FormItem class="mb-2">
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input
                  type="text"
                  placeholder="Enter your password"
                  v-bind="componentField"
                />
              </FormControl>
              <FormDescription>
                Must be at least 8 characters long.
              </FormDescription>
              <FormMessage />
            </FormItem>
          </FormField>
          <FormField v-slot="{ componentField }" name="date_of_birth">
            <FormItem class="my-2.5">
              <FormLabel>Date of Birth</FormLabel>
              <FormControl>
                <DatePicker v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
          <Button class="mt-3" type="submit"> Create Account </Button>
        </form>
      </CardContent>
      <CardFooter class="flex flex-col">
        <span class="mb-1 text-sm text-gray-400">Already have an account?</span>
        <Button variant="outline" class="w-full" @click="navigateToLogin"
          >Login</Button
        >
      </CardFooter>
    </Card>
    <FieldDescription class="px-6 text-center">
      By clicking continue, you agree to our
      <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
    </FieldDescription>
  </div>
</template>
