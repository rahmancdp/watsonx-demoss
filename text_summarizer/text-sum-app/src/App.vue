<template>
  <div>
    <CvHeader aria-label="Header">
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
      <CvHeaderName>Text Summariser with Watsonx</CvHeaderName>
      <CvHeaderNavigation :expanded="isMenuExpanded">
      </CvHeaderNavigation>
    </CvHeader>
    <div class="container">
      <CvTitle size="xl">LangChain Text Summariser with Watsonx</CvTitle>
      <div class="text-area-container">
        <CvTextArea v-model="sourceText" label="Enter the source text" rows="10" cols="50" />
        <CvTextArea v-model="summary" label="Summary will appear here" rows="10" cols="50" readonly />
      </div>
      <CvButton @click="summarize">Summarize</CvButton>
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
      isMenuExpanded: false,
    };
  },
  methods: {
    toggleMenu() {
      this.isMenuExpanded = !this.isMenuExpanded;
    },
    async summarize() {
      try {
        const response = await axios.post('http://localhost:8000/summarize', {
          source_text: this.sourceText,
        });

        this.summary = response.data.summary;
      } catch (error) {
        console.error(error);
      }
    },
  },
};
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