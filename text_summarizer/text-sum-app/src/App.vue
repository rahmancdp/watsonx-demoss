<template>
  <div>
    <CvHeader aria-label="Header">
      <CvHeaderGlobalAction>
        <!-- Global action content here -->
      </CvHeaderGlobalAction>
      <CvHeaderMenuButton @click="toggleMenu" :expanded="isMenuExpanded" />
      <CvHeaderName prefix="LangChain">Text Summariser with Watsonx</CvHeaderName>
      <CvHeaderNavigation :expanded="isMenuExpanded">
        <CvHeaderMenuItem>
          <CvHeaderMenuItemButton>
            <CvHeaderMenuIcon>
              <!-- Add your icon component or SVG here -->
            </CvHeaderMenuIcon>
            Home
          </CvHeaderMenuItemButton>
        </CvHeaderMenuItem>
        <CvHeaderMenuItem>
          <CvHeaderMenuItemButton>
            <CvHeaderMenuIcon>
              <!-- Add your icon component or SVG here -->
            </CvHeaderMenuIcon>
            About
          </CvHeaderMenuItemButton>
        </CvHeaderMenuItem>
        <!-- Add more menu items as needed -->
      </CvHeaderNavigation>
    </CvHeader>
    <div class="container">
      <CvTitle size="xl">LangChain Text Summariser with Watsonx</CvTitle>
      <div class="text-area-container">
        <CvTextArea v-model="sourceText" label="Enter the source text" rows="10" cols="50" />
        <CvTextArea v-model="summary" label="Summary will appear here" rows="10" cols="50" readonly />
      </div>
      <CvButton @click="summarize">Summarize</CvButton>
    </div>
  </div>
</template>

<script>
import { CvTitle, CvButton, CvTextArea, CvHeader, CvHeaderGlobalAction, CvHeaderMenuButton, CvHeaderName, CvHeaderNavigation, CvHeaderMenuItem, CvHeaderMenuItemButton, CvHeaderMenuIcon } from '@carbon/vue';
import axios from 'axios';

export default {
  components: {
    CvHeader,
    CvHeaderGlobalAction,
    CvHeaderMenuButton,
    CvHeaderName,
    CvHeaderNavigation,
    CvHeaderMenuItem,
    CvHeaderMenuItemButton,
    CvHeaderMenuIcon,
    CvTitle,
    CvButton,
    CvTextArea,
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

.text-area-container {
  display: flex;
  gap: 20px;
}
</style>