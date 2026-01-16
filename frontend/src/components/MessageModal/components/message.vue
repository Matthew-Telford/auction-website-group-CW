<script setup lang="ts">
import { ref } from "vue";
import { Card, CardContent } from "@/components/ui/card";
import { Message } from "../MessageModal.types";
import { CornerDownLeft, BadgeCheck, Trash } from "lucide-vue-next";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useUserStore } from "@/stores/userStore";
import { calculateDaysAgo } from "@/utils/date";

const props = defineProps<{
  message: Message;
}>();

const emit = defineEmits<{
  (e: "reply", message: Omit<Message, "replies">): void;
  (e: "delete", messageId: string): void;
}>();

const userStore = useUserStore();
const showDeleteDialog = ref(false);
const messageToDelete = ref<string | undefined>(undefined);

const handleReply = () => {
  const { replies, ...messageWithoutReplies } = props.message;
  emit("reply", messageWithoutReplies);
};

const openDeleteDialog = (messageId: string) => {
  messageToDelete.value = messageId;
  showDeleteDialog.value = true;
};

const handleDelete = () => {
  if (messageToDelete.value) {
    emit("delete", messageToDelete.value);
  }
  showDeleteDialog.value = false;
  messageToDelete.value = undefined;
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};
</script>

<template>
  <Card class="mb-3 w-2/3">
    <CardContent class="">
      <div class="flex justify-between items-start mb-1">
        <div>
          <div class="flex items-center gap-1 mb-1">
            <span class="text-sm font-medium">{{
              props.message.poster?.name || "Unknown"
            }}</span>
            <TooltipProvider v-if="props.message.is_owner">
              <Tooltip>
                <TooltipTrigger as-child>
                  <BadgeCheck class="w-3.5 h-3.5 text-primary" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Item Owner</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <span class="text-xs text-muted-foreground">
            {{ calculateDaysAgo(props.message.created_at) }}
            {{
              calculateDaysAgo(props.message.created_at) === 1 ? "day" : "days"
            }}
            ago
          </span>
        </div>

        <div class="flex items-center gap-1">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger as-child>
                <button
                  class="p-1 hover:bg-muted rounded-md transition-colors"
                  @click="handleReply"
                >
                  <CornerDownLeft class="w-3.5 h-3.5 text-muted-foreground" />
                </button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Reply</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider
            v-if="
              userStore.user &&
              props.message.poster &&
              userStore.user.id === props.message.poster.id
            "
          >
            <Tooltip>
              <TooltipTrigger as-child>
                <button
                  class="p-1 hover:bg-destructive/10 rounded-md transition-colors group"
                  @click="openDeleteDialog(props.message.id)"
                >
                  <Trash
                    class="w-3.5 h-3.5 text-muted-foreground group-hover:text-destructive transition-colors"
                  />
                </button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Delete</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>

      <div class="mb-2">
        <p class="text-sm leading-snug">{{ props.message.message_body }}</p>
      </div>

      <div
        v-if="props.message.replies && props.message.replies.length > 0"
        class="mt-4 pl-6 space-y-3 border-l-2 border-muted"
      >
        <div
          v-for="reply in props.message.replies"
          :key="reply.id"
          class="space-y-1"
        >
          <p class="text-sm leading-relaxed text-muted-foreground">
            {{ reply.message_body }}
          </p>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1">
              <span class="text-xs font-medium text-muted-foreground">{{
                reply.poster?.name || "Unknown"
              }}</span>
              <TooltipProvider v-if="reply.is_owner">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <BadgeCheck class="w-3 h-3 text-primary" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Item Owner</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <div class="flex items-center gap-1">
              <span class="text-xs text-muted-foreground">{{
                formatDate(reply.created_at)
              }}</span>

              <TooltipProvider
                v-if="
                  userStore.user &&
                  reply.poster &&
                  userStore.user.id === reply.poster.id
                "
              >
                <Tooltip>
                  <TooltipTrigger as-child>
                    <button
                      class="p-0.5 hover:bg-destructive/10 rounded-md transition-colors group"
                      @click="openDeleteDialog(reply.id)"
                    >
                      <Trash
                        class="w-3 h-3 text-muted-foreground group-hover:text-destructive transition-colors"
                      />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Delete</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
        </div>
      </div>
    </CardContent>

    <Dialog v-model:open="showDeleteDialog">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Delete Message</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete this message? This action
            cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter class="gap-2 sm:gap-0">
          <Button
            class="mr-1"
            variant="outline"
            @click="showDeleteDialog = false"
          >
            Close
          </Button>
          <Button variant="destructive" @click="handleDelete">
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </Card>
</template>
