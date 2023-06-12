<script setup>
import { ref } from 'vue';
import axios from 'axios';
import Table from './components/Table.vue';

const title = ref('');
const keyword = ref('');
const fileInput = ref(null);
const extractedText = ref('');
const overlay = ref(false);
const loading = ref(false);

const onClick = () => {
  loading.value = true;
  overlay.value = true;
  axios
    .post('http://127.0.0.1:5000/search', { keyword: keyword.value })
    .then(res => {
      if (res.data.status == 200) {
        console.log(res.data);
        loading.value = false;
        overlay.value = false;
        extractedText.value = res.data.data;
        title.value = res.data.file_name;
      }
    })
    .catch(err => {
      console.log(err);
    });
};

const handleFile = async event => {
  overlay.value = true;
  const file = event.target.files[0];
  const formData = new FormData();
  formData.append('pdf_file', file);
  axios
    .post('http://127.0.0.1:5000/upload', formData)
    .then(res => {
      if (res.data.status == 200) {
        console.log(res.data);
        overlay.value = false;
        extractedText.value = res.data.data;
        title.value = res.data.file_name;
      }
      console.log(extractedText.value);
    })
    .catch(err => {
      console.log(err);
    });
  fileInput.value.reset();
};
</script>

<template>
  <v-app>
    <v-app-bar app dark>
      <h1>論文摘要系統</h1>
    </v-app-bar>
    <v-main>
      <v-overlay
        :model-value="overlay"
        class="align-center justify-center"
        persistent
      >
        <v-progress-circular
          color="primary"
          indeterminate
          size="64"
        ></v-progress-circular>
      </v-overlay>
      <div class="d-flex justify-center" fluid>
        <v-row justify="center">
          <v-col cols="12">
            <v-card class="mx-auto" color="grey-lighten-3" max-width="400">
              <v-card-text>
                <v-text-field
                  v-model="keyword"
                  :loading="loading"
                  density="compact"
                  variant="solo"
                  label="Search templates"
                  append-inner-icon="mdi-magnify"
                  single-line
                  hide-details
                  @click:append-inner="onClick"
                ></v-text-field>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" class="d-flex justify-center">
            <v-card class="mx-auto">
              <v-card-text>
                <v-file-input
                  ref="fileInput"
                  class="input"
                  @change="handleFile"
                  label="File input"
                  variant="solo-filled"
                ></v-file-input>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12">
            <Table :summary="extractedText" :title="title" />
          </v-col>
        </v-row>
      </div>
      <div class="d-flex justify-center ma-4">
        <v-alert v-if="error" type="error" variant="outlined">
          {{ error }}
        </v-alert>
      </div>
    </v-main>
    <v-footer app class="justify-center"></v-footer>
  </v-app>
</template>

<style scoped>
.input {
  width: 746.4px;
}

h1 {
  color: #fff;
  letter-spacing: 0.1em;
  font-family: 'Roboto', sans-serif;
  padding-left: 45px;
}
</style>
