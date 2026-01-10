<script setup lang="ts">
import { ref, onMounted, defineModel } from "vue";
import { useForm } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import * as z from "zod";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

const emit = defineEmits<{
  (e: "loginPressed", email: string, password: string): void;
  (e: "signupPressed"): void;
}>();

const loginValidationSchema = toTypedSchema(
  z.object({
    email: z
      .string()
      .min(1, { message: "Email must not be blank" })
      .email("Invalid Email Address"),

    password: z.string().min(8, { message: "Minimum password length is 8" }),
  }),
);

const loginForm = useForm({
  validationSchema: loginValidationSchema,
});

const onSubmit = loginForm.handleSubmit((email, password) => {
  emit("loginPressed", email, password);
});

const handleSignup = () => {
  emit("signupPressed");
};

//const errors = defineModel<JSON>();
</script>

<template>
  <Card class="w-full max-w-sm">
    <CardHeader>
      <CardTitle> Login to your account </CardTitle>
      <CardDescription>Enter your email and password below</CardDescription>
    </CardHeader>
    <CardContent>
      <form @submit="onSubmit">
        <FormField v-slot="{ componentField }" name="email">
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input
                class="mb-2"
                type="text"
                placeholder="Enter your email"
                v-bind="componentField"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="password">
          <FormItem>
            <FormLabel>Password</FormLabel>
            <FormControl>
              <Input
                class="mb-2"
                type="text"
                placeholder="Enter your password"
                v-bind="componentField"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <Button class="mt-1" type="submit">Login</Button>
      </form>
    </CardContent>
    <CardFooter class="flex flex-col">
      <span class="text-sm text-gray-400">Don't have an account?</span>
      <Button variant="outline" class="w-full" @click="handleSignup"
        >Signup</Button
      >
    </CardFooter>
  </Card>
</template>
