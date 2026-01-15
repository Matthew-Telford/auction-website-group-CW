<template>
    <form @submit.prevent="submitForm" class="space-y-4">
      <div>
        <label>Title</label>
        <input v-model="form.title" required />
      </div>
  
      <div>
        <label>Description</label>
        <textarea v-model="form.description" required></textarea>
      </div>
  
      <div>
        <label>Starting Price</label>
        <input type="number" v-model.number="form.starting_price" required />
      </div>
  
      <div>
        <label>End Date</label>
        <input type="datetime-local" v-model="form.end_datetime" required />
      </div>
  
      <div>
        <label>Image</label>
        <input type="file" @change="onFileChange" required />
      </div>
  
      <button type="submit">Create Auction</button>
  
      <p v-if="message">{{ message }}</p>
    </form>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from "vue";
  
  export default defineComponent({
    setup() {
      const form = ref({
        title: "",
        description: "",
        starting_price: 0,
        end_datetime: "",
        image: null as File | null,
      });
  
      const message = ref("");
  
      const onFileChange = (e: Event) => {
        const input = e.target as HTMLInputElement;
        if (input.files?.length) {
          form.value.image = input.files[0];
        }
      };
  
      const submitForm = async () => {
        const formData = new FormData();
        Object.entries(form.value).forEach(([key, value]) => {
          if (value !== null) {
            formData.append(key, value.toString());
          }
        });
  
        if (form.value.image) {
          formData.set("image", form.value.image);
        }
  
        const response = await fetch("/items/create/", {
          method: "POST",
          credentials: "include",
          headers: {
            "X-CSRFToken": document.cookie
              .split("; ")
              .find(row => row.startsWith("csrftoken="))
              ?.split("=")[1] || "",
          },
          body: formData,
        });
  
        message.value = response.ok
          ? "Auction created"
          : "Something went wrong";
      };
  
      return { form, message, onFileChange, submitForm };
    },
  });
  </script>