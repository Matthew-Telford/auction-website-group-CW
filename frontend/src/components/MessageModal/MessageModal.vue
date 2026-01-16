<script setup lang="ts">
import { ref, computed } from "vue";
import { toast } from "vue-sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send } from "lucide-vue-next";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import MessageComponent from "./components/message.vue";
import { Message } from "./MessageModal.types";
import { useUserStore } from "@/stores/userStore";
import { getCSRFToken } from "@/utils/csrf";

const props = defineProps<{
  itemId: string;
  itemTitle: string;
  messages?: Message[];
}>();

const emit = defineEmits<{
  messagesUpdated: [];
}>();

const userStore = useUserStore();

const isOpen = ref(false);
const messageInput = ref("");
const isReplying = ref(false);
const replyingToMessage = ref<Omit<Message, "replies"> | null>(null);

const inputPlaceholder = computed(() => {
  return userStore.isLoggedIn
    ? "Send a message"
    : "Must be logged in to send messages";
});

const handleReply = (message: Omit<Message, "replies">) => {
  isReplying.value = true;
  replyingToMessage.value = message;
};

const cancelReply = () => {
  isReplying.value = false;
  replyingToMessage.value = null;
};

const handleSendMessage = async () => {
  if (!messageInput.value.trim()) {
    toast.error("Message cannot be empty", {
      action: {
        label: "Close",
        onClick: () => {},
      },
    });
    return;
  }

  const csrfToken = getCSRFToken();

  try {
    const requestBody: {
      item_id: string;
      message_title: string;
      message_body: string;
      replying_to_id?: string;
    } = {
      item_id: props.itemId,
      message_title: isReplying.value && replyingToMessage.value
        ? `Re: ${replyingToMessage.value.message_title}`
        : "Message",
      message_body: messageInput.value,
    };

    if (isReplying.value && replyingToMessage.value) {
      requestBody.replying_to_id = replyingToMessage.value.id;
    }

    const fetchResults = await fetch("http://localhost:8000/messages/create/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken ?? "",
      },
      credentials: "include",
      body: JSON.stringify(requestBody),
    });

    if (!fetchResults.ok) {
      const errorData = await fetchResults.json().catch(() => ({}));
      toast.error(errorData.error || "Failed to send message", {
        action: {
          label: "Close",
          onClick: () => {},
        },
      });
      return;
    }

    const result = await fetchResults.json();

    if (result.success) {
      toast.success("Message sent successfully!", {
        action: {
          label: "Close",
          onClick: () => {},
        },
      });
      messageInput.value = "";
      cancelReply();
      emit("messagesUpdated");
    } else {
      toast.error(result.error || "Failed to send message", {
        action: {
          label: "Close",
          onClick: () => {},
        },
      });
    }
  } catch (err) {
    console.error("Error sending message:", err);
    toast.error("An error occurred while sending the message", {
      action: {
        label: "Close",
        onClick: () => {},
      },
    });
  }
};

const handleDeleteMessage = async (messageId: string) => {
  try {
    const fetchResults = await fetch(
      `http://localhost:8000/messages/${messageId}/delete/`,
      {
        method: "DELETE",
        credentials: "include",
      },
    );

    if (!fetchResults.ok) {
      const errorData = await fetchResults.json().catch(() => ({}));
      toast.error(errorData.error || "Failed to delete message", {
        action: {
          label: "Close",
          onClick: () => {},
        },
      });
      return;
    }

    const result = await fetchResults.json();

    if (result.success) {
      emit("messagesUpdated");
    } else {
      toast.error(result.error || "Failed to delete message", {
        action: {
          label: "Close",
          onClick: () => {},
        },
      });
    }
  } catch (err) {
    console.error("Error deleting message:", err);
    toast.error("An error occurred while deleting the message", {
      action: {
        label: "Close",
        onClick: () => {},
      },
    });
  }
};

defineExpose({
  isOpen,
});
</script>

<template>
  <Dialog v-model:open="isOpen">
    <DialogTrigger as-child>
      <slot />
    </DialogTrigger>
    <DialogContent class="sm:max-w-[700px] h-[80vh] flex flex-col p-0">
      <DialogHeader class="px-6 pt-6">
        <DialogTitle>{{ props.itemTitle }}</DialogTitle>
        <DialogDescription class="mt-2"
          >Messages about this item</DialogDescription
        >
      </DialogHeader>

      <ScrollArea class="flex-1 px-6">
        <div
          v-if="!props.messages?.length"
          class="flex items-center justify-center h-full text-muted-foreground text-sm pt-8"
        >
          No messages yet. Start the conversation!
        </div>
        <div v-else class="space-y-3 py-4">
          <MessageComponent
            v-for="message in props.messages"
            :key="message.id"
            :message="message"
            @reply="handleReply"
            @delete="handleDeleteMessage"
          />
        </div>
      </ScrollArea>

      <div class="border-t shadow-[0_-2px_10px_rgba(0,0,0,0.05)] px-6 py-4">
        <div
          v-if="isReplying && replyingToMessage"
          class="mb-2 flex items-center justify-between"
        >
          <span class="text-xs text-muted-foreground">
            Replying to {{ replyingToMessage.poster?.name || "Unknown" }}
          </span>
          <button
            @click="cancelReply"
            class="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Cancel
          </button>
        </div>
        <div class="flex items-center gap-2">
          <Input
            v-model="messageInput"
            :placeholder="inputPlaceholder"
            :disabled="!userStore.isLoggedIn"
            class="flex-1 bg-transparent border-input"
            @keydown.enter="handleSendMessage"
          />
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger as-child>
                <button
                  class="p-2 hover:bg-muted rounded-md transition-colors"
                  :disabled="!userStore.isLoggedIn"
                  @click="handleSendMessage"
                >
                  <Send class="w-5 h-5 text-muted-foreground" />
                </button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Send</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
