<script setup lang="ts">
import { useRouter } from "vue-router";
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
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

const router = useRouter();

const emit = defineEmits<{
  (e: "loginPressed", email: string, password: string): void;
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

const onSubmit = loginForm.handleSubmit((values) => {
  console.log("email:", values.email);
  console.log("password:", values.password);
  emit("loginPressed", values.email, values.password);
});

const handleSignup = () => {
  router.push("/signup");
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
                type="text"
                placeholder="Enter your email"
                v-bind="componentField"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="password">
          <FormItem class="mt-2">
            <FormLabel>Password</FormLabel>
            <FormControl>
              <Input
                type="text"
                placeholder="Enter your password"
                v-bind="componentField"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <div class="flex flex-col justify-center items-center w-full">
          <Button class="mt-2" type="submit">Login</Button>
        </div>
      </form>
    </CardContent>
    <CardFooter class="flex flex-col">
      <span class="text-sm text-gray-400 mb-1">Don't have an account?</span>
      <Button variant="outline" class="w-full" @click="handleSignup"
        >Signup</Button
      >
    </CardFooter>
  </Card>
</template>
