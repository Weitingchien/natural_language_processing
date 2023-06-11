<template>
  <div>
    <v-table>
      <thead>
        <tr>
          <th class="text-left">title</th>
          <th class="text-left">summary</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in summaries" :key="item.title">
          <td>{{ item.title }}</td>
          <td>{{ item.summary }}</td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<script setup>
import { watch, reactive } from 'vue';

const props = defineProps({
  title: { type: String, default: 'Default Title' },
  summary: { type: String, default: 'Default Summary' }
});

watch(
  () => props.title,
  () => {
    summaries.push({
      title: props.title,
      summary: props.summary
    });
  }
);

const summaries = reactive([]);
</script>
