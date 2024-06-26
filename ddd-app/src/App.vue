<template>
  <div>
    <CvHeader aria-label="Header">
      <CvHeaderName>DDD Java Generator with Watsonx</CvHeaderName>
      <CvHeaderGlobalAction aria-label="Notifications">
        <Notification20/>
        <!-- Global action content here -->
      </CvHeaderGlobalAction>
      <CvHeaderGlobalAction aria-label="UserAvatar">
        <UserAvatar20/>
        <!-- Global action content here -->
      </CvHeaderGlobalAction>
      <CvHeaderGlobalAction aria-label="AppSwitcher20">
        <AppSwitcher20/>
        <!-- Global action content here -->
      </CvHeaderGlobalAction>
      <CvHeaderMenuButton @click="toggleMenu" :expanded="isMenuExpanded" />
      <CvHeaderNavigation :expanded="isMenuExpanded">
      </CvHeaderNavigation>
    </CvHeader>
    <div class="container">
      <CvTitle size="xl">DDD Java Generator with Watsonx</CvTitle>
      <div class="text-area-container">
        <CvTextArea v-model="sourceText" label="Enter the source text" rows="10" cols="50" />
        <CvTextArea v-model="summary" label="Summary will appear here" rows="10" cols="50" readonly />
      </div>
      <CvButton @click="summarize">Summarize</CvButton>
      <CvButton @click="generate">Generate</CvButton>
      <CvButton @click="generate">Propose Domain Entity</CvButton>
      <CvButton @click="generate">Propose Method</CvButton>
      <CvButton @click="generate">Generate DDD Code</CvButton>
      <div class="side-rail">
        <!-- Side rail content here -->
      </div>
    </div>
  </div>
</template>

<script>
import { CvTitle, CvButton, CvTextArea, CvHeader, CvHeaderGlobalAction, CvHeaderMenuButton, CvHeaderName, CvHeaderNavigation } from '@carbon/vue';
import axios from 'axios';
import { Notification20, UserAvatar20, AppSwitcher20 } from '@carbon/icons-vue';

export default {
  components: {
    CvHeader,
    CvHeaderGlobalAction,
    CvHeaderMenuButton,
    CvHeaderName,
    CvHeaderNavigation,
    CvTitle,
    CvButton,
    CvTextArea,
    Notification20,
    UserAvatar20,
    AppSwitcher20
  },
  data() {
    return {
      sourceText: '',
      summary: '',
      streaming: false,
    };
  },
  methods: {
    toggleMenu() {
      this.isMenuExpanded = !this.isMenuExpanded;
    },
    async generate() {
      if (this.streaming) return;

      this.streaming = true;

      try {
        await this.fetchStreamData();
      } catch (error) {
        console.error(error);
        this.summary = 'Error occurred during generation';
      } finally {
        this.streaming = false;
      }
    },
    async fetchStreamData() {
      const response = await axios.post(`http://localhost:8000/stream`, { stream: true }, { responseType: 'text' });
      const reader = response.data.getReader();
      let fullResponse = '';

      const readChunk = async () => {
        console.log('reading')
        const { done, value } = await reader.read();
        print(value)
        if (done) {
          console.log('done')
          this.streaming = false;
          return;
        }

        const partialMessage = new TextDecoder('utf-8').decode(value);
        fullResponse += partialMessage;

        this.summary = fullResponse;
        console.log(fullResponse);

        await readChunk();
      };

      await readChunk();
    },
    summarize() {
      this.streaming = true;

      this.summary = 'Summarizing...';

      const socket = new WebSocket(`ws://localhost:8000/websocket?source_text=${encodeURIComponent(this.sourceText)}`);

      socket.onopen = () => {
        console.log("WebSocket connection established");
        socket.send("start-streaming");
      };

      socket.onmessage = (event) => {
        const text = event.data;
        this.summary += text;
      };

      socket.onclose = () => {
        console.log("WebSocket connection closed");
        this.streaming = false;
      };
    },
    async summarize1() {
      try {
        this.summary = 'Summarizing...';
        const response = await axios.post('http://localhost:8000/summarize', {
          source_text: this.sourceText,
        });

        const stream = response.data.stream;
        stream.onmessage = (event) => {
          this.summary += event.data;
        };

        stream.onerror = (event) => {
          console.error('Error occurred in stream:', event);
        };

        stream.onclose = () => {
          console.log('Stream closed');
        };

        // const response = await axios.post('http://localhost:8000/summarize', {
        //   source_text: this.sourceText,
        // });

        // this.summary = response.data.summary;
      } catch (error) {
        console.error(error);
      }
    },
  },
}
</script>

<style lang="scss">
@import "./styles/carbon";

.container {
  padding: 20px;
  padding-top: 60px; /* Add padding to the top */
}

.side-rail {
  flex-basis: 300px; /* Adjust the width as needed */
  /* Add styling for the side rail */
}

.text-area-container {
  display: flex;
  gap: 20px;
}
</style>
