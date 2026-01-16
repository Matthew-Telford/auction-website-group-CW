<script setup lang="ts">
    import { ref, watch } from "vue";
    import { useForm } from "vee-validate";
    import { toTypedSchema } from "@vee-validate/zod";
    import * as z from "zod";
    import { Button } from "@/components/ui/button";
    import { Input } from "@/components/ui/input";
    import { Label } from "@/components/ui/label";
    import {
      Dialog,
      DialogContent,
      DialogDescription,
      DialogFooter,
      DialogHeader,
      DialogTitle,
      DialogTrigger,
    } from "@/components/ui/dialog";
    import {
      FormControl,
      FormField,
      FormItem,
      FormLabel,
      FormMessage,
    } from "@/components/ui/form";
    
    const props = defineProps<{
      initialData: any;
    }>();
    
    const emit = defineEmits<{ 
        (e: "save", payload: { profile_picture: File; email: string }): void;
    }>()
    const isOpen = ref(false);
    const previewUrl = ref<string | null>(null);
    const image=ref<File | null>(null);
    
    // Validation Schema
    const formSchema = toTypedSchema(
      z.object({
        email: z.string().email(),
        first_name: z.string().optional(),
        last_name: z.string().optional(),
        date_of_birth: z.string().optional(),
      })
    );
    
    const form = useForm({
      validationSchema: formSchema,
    });
    
    // Watch for data changes to pre-fill form
    watch(() => props.initialData, (newData) => {
      if (newData) {
        form.setValues({
          email: newData.email,
          first_name: newData.first_name,
          last_name: newData.last_name,
          date_of_birth: newData.date_of_birth,
        });
        previewUrl.value = newData.profile_image;
      }
    });
    
    const onFileChange = async (e: Event) => {
      const target = e.target as HTMLInputElement;
      if (target.files && target.files[0]) {
        /*
        const file = target.files[0];
        // Convert to Base64 immediately for preview AND sending
        const base64String = await fileToBase64(file);
        previewUrl.value = base64String; 
        */
       image.value=target.files[0];
       previewUrl.value=URL.createObjectURL(image.value);
      }
    };
    
    const onSubmit = form.handleSubmit(() => {
      if (image.value) {
        emit("save", {
          profile_picture: image.value,
          email: form.values.email || ""
        });
      }
      isOpen.value = false; // Close modal
    });
    </script>
    
    <template>
      <Dialog v-model:open="isOpen">
        <DialogTrigger as-child>
          <Button variant="outline">Edit Profile</Button>
        </DialogTrigger>
        <DialogContent class="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit profile</DialogTitle>
            <DialogDescription>
              Make changes to your profile here. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          
          <form @submit="onSubmit" class="grid gap-4 py-4">
            <div class="flex flex-col items-center gap-4">
              <img 
                :src="previewUrl || '/placeholder-user.jpg'" 
                class="w-24 h-24 rounded-full object-cover border" 
              />
              <div class="grid w-full max-w-sm items-center gap-1.5">
                <Label htmlFor="picture">Profile Picture</Label>
                <Input id="picture" type="file" accept="image/*" @change="onFileChange" />
              </div>
            </div>
    
            <FormField v-slot="{ componentField }" name="email">
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input v-bind="componentField" />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
    
            <div class="grid grid-cols-2 gap-4">
              <FormField v-slot="{ componentField }" name="first_name">
                <FormItem>
                  <FormLabel>First Name</FormLabel>
                  <FormControl><Input v-bind="componentField" /></FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>
              
              <FormField v-slot="{ componentField }" name="last_name">
                <FormItem>
                  <FormLabel>Last Name</FormLabel>
                  <FormControl><Input v-bind="componentField" /></FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>
            </div>
    
            <FormField v-slot="{ componentField }" name="date_of_birth">
              <FormItem>
                <FormLabel>Date of Birth</FormLabel>
                <FormControl>
                  <Input type="date" v-bind="componentField" />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
    
            <DialogFooter>
              <Button type="submit">Save changes</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </template>