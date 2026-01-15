<template>
  <div class="auction-create container mx-auto p-6">
    <h1 class="text-2xl font-bold mb-4">Create New Auction</h1>

    <form @submit.prevent="submitForm" class="space-y-4">
      <div>
        <label class="block mb-1">Title</label>
        <input v-model="form.title" type="text" class="input" required />
      </div>

      <div>
        <label class="block mb-1">Description</label>
        <textarea v-model="form.description" class="input" rows="4" required></textarea>
      </div>

      <div>
        <label class="block mb-1">Starting Price</label>
        <input v-model.number="form.starting_price" type="number" class="input" required />
      </div>

      <div>
        <label class="block mb-1">End Date/Time</label>
        <input v-model="form.end_datetime" type="datetime-local" class="input" required />
      </div>

      <div>
        <label class="block mb-1">Image</label>
        <input type="file" @change="onFileChange" accept="image/*" required />
      </div>

      <button type="submit" class="btn btn-primary">Create Auction</button>
    </form>

    <p v-if="message" class="mt-4">{{ message }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

interface AuctionForm {
  title: string
  description: string
  starting_price: number
  end_datetime: string
  image: File | null
}

export default defineComponent({
  name: 'AuctionCreate',
  setup() {
    const form = ref<AuctionForm>({
      title: '',
      description: '',
      starting_price: 0,
      end_datetime: '',
      image: null
    })

    const message = ref<string>('')

    const onFileChange = (e: Event) => {
      const target = e.target as HTMLInputElement
      if (target.files && target.files.length > 0) {
        form.value.image = target.files[0]
      }
    }

    const submitForm = async () => {
      const formData = new FormData()
      formData.append('title', form.value.title)
      formData.append('description', form.value.description)
      formData.append('starting_price', form.value.starting_price.toString())
      formData.append('end_datetime', form.value.end_datetime)
      if (form.value.image) formData.append('image', form.value.image)

      try {
        const response = await fetch('/items/create/', {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': getCookie('csrftoken')
          }
        })

        if (!response.ok) throw new Error('Failed to create auction')
        message.value = 'Auction created successfully!'
      } catch (error) {
        message.value = (error as Error).message
      }
    }

    const getCookie = (name: string): string => {
      const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
      return match ? match[2] : ''
    }

    return { form, onFileChange, submitForm, message }
  }
})
</script>

<style scoped>
.input {
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px;
}
.btn {
  background-color: #007bff;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
}
</style>