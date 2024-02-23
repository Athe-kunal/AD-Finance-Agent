<template>
  <div class="chat-container">
    <context-holder></context-holder>
    <a-modal v-model:open="open" :title="pdfTitle" @ok="handleOk">
      <vue-pdf-app style="height: 400px" :pdf="this.pdfPath"></vue-pdf-app>
    </a-modal>
    <div class="chat-messages" ref="chatMessages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="message"
        :class="{
          'user-message': message.sender === 'user',
          'ai-message': message.sender === 'ai'
        }"
      >
        <div class="message-title">
          <div class="icon">
            <BorderlessTableOutlined v-if="message.sender === 'ai'" />
            <UserOutlined v-else />
          </div>
          <h6 class="message-user">
            <span v-if="message.sender === 'ai'">Aswath Damodaran Bot: {{ message.model }}</span>
            <span v-else>You</span>
          </h6>
        </div>
        <div class="loading-container" v-if="message.text === 'loading' && message.sender === 'ai'">
          <div class="loading-dots dot1">&#9679;</div>
          <div class="loading-dots dot2">&#9679;</div>
          <div class="loading-dots dot3">&#9679;</div>
        </div>
        <div v-else class="message-response">
          <span>{{ message.text }}</span>

          <div class="resources" v-if="message.sender === 'ai' && message.resources">
            <!-- <h3 class="resources-text">Resources</h3> -->
            <div
              class="resource"
              v-for="(resource, index) in message.resources"
              :key="index"
              @click="openModal(resource)"
            >
              <FileTextOutlined style="font-size: 40px" v-if="resource.bookURL" />
              <YoutubeOutlined style="font-size: 40px" v-else />
              <p style="margin: 5px 5px 0; text-decoration: underline" v-if="resource.bookURL">
                {{ resource.book_source }}
              </p>
              <p style="margin-bottom: 0; margin-top: 5px; text-decoration: underline" v-else>
                <a :href="createYoutubeLink(resource)" target="_blank">Watch Video</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <input
        v-model="userInput"
        @keyup.enter="sendMessage"
        placeholder="Type your message here..."
      />
      <button @click="sendMessage">
        <SendOutlined />
      </button>
    </div>
  </div>
</template>

<script>
import {
  BorderlessTableOutlined,
  UserOutlined,
  SendOutlined,
  FileTextOutlined,
  YoutubeOutlined
} from '@ant-design/icons-vue'
import { useModelStore } from '@/stores/counter'
import { message } from 'ant-design-vue'
import VuePdfApp from 'vue3-pdf-app'
import 'vue3-pdf-app/dist/icons/main.css'
const [messageApi, contextHolder] = message.useMessage()

export default {
  data() {
    return {
      userInput: '',
      messages: [],
      store: useModelStore(),
      resources: [],
      open: false,
      pdfPath: ''
    }
  },
  components: {
    BorderlessTableOutlined,
    UserOutlined,
    SendOutlined,
    FileTextOutlined,
    contextHolder,
    VuePdfApp,
    YoutubeOutlined
  },
  methods: {
    async sendMessage() {
      if (this.userInput.trim() !== '') {
        if (!this.store.model) {
          messageApi.error('Please select a model!')
          return
        }
        this.messages.push({ text: this.userInput, sender: 'user' })
        this.messages.push({ text: 'loading', model: this.store.model, sender: 'ai' })
        this.$nextTick(() => {
          this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.clientHeight
        })
        const query = this.userInput
        this.userInput = ''
        const answer = await this.getQuery(query)
        this.messages.pop()
        this.messages.push({
          text: answer.response,
          resources: answer.metaData,
          model: this.store.model,
          sender: 'ai'
        })
        this.$nextTick(() => {
          this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.clientHeight
        })
      }
    },
    async getQuery(query) {
      const response = await fetch(
        'http://127.0.0.1:5000' + '/query?query= ' + query + '&model=' + this.store.model
      )
      const details = await response.json()
      return details
    },
    handleOk() {
      this.open = false
    },
    openModal(resource) {
      if (resource.youtube_id) return
      this.pdfPath = resource.bookURL
      this.pdfTitle = resource.book_source
      console.log(this.pdfPath)
      this.open = true
    },
    createYoutubeLink(resource) {
      let sec = Math.floor(parseFloat(resource.start_timestamp) * 60)
      return `https://www.youtube.com/watch?v=${resource.youtube_id}&t=${sec}`
    }
  }
}
</script>

<style scoped lang="scss">
.chat-container {
  min-height: 90vh;
  width: 700px;
  display: flex;
  flex-direction: column;
  justify-content: end;
}

.chat-messages {
  max-height: 80vh;
  overflow-x: auto;
  padding: 10px;
}

.message {
  margin-bottom: 30px;
  padding: 8px 12px;
  // border-radius: 5px;

  &-title {
    display: flex;
    align-items: baseline;
  }

  &-user {
    font-size: 18px;
    font-weight: 600;
    padding-inline-start: 10px;
  }
}

.chat-input {
  display: flex;
  align-items: center;
  padding: 10px;
}

.chat-input input {
  flex: 1;
  padding: 8px;
  border-radius: 5px;
  border: 1px solid #ccc;

  &:focus-visible {
    outline: none;
    border: 1px solid #2ecc71 !important;
    box-shadow: 0 0 0 1px rgba(#2ecc71, 0.2) !important;
  }
}

.chat-input button {
  padding: 8px 12px;
  margin-left: 10px;
  border-radius: 5px;
  border: none;
  background-color: #2ecc71;
  color: white;
  cursor: pointer;
}

.icon {
  // background-color: white;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
  width: 30px;
  height: 30px;
  border-radius: 50%;

  display: flex;
  justify-content: center;
  align-items: center;

  background-color: #2ecc71; /* Green shade */
  color: #fff; /* Text color */
}

.loading-container {
  text-align: center;
  // margin-top: 50px;
  display: flex;
}

.loading-dots {
  font-size: 12px;
  margin-left: 10px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

.dot1 {
  animation-delay: 0.2s;
}

.dot2 {
  animation-delay: 0.4s;
}

.dot3 {
  animation-delay: 0.6s;
}

.resources {
  display: flex;
  max-width: 700px;
  overflow-x: auto;
}

.resource {
  min-width: 200px;
  height: 100px;
  margin-right: 10px;
  margin-top: 20px;
  padding: 20px;
  border-radius: 10px;

  background-color: white;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  cursor: pointer;
}
</style>
