/**
 * Video Player Component
 * Maneja el tracking de progreso de videos
 */

import { api } from '../core/api.js';
import { DOM } from '../utils/dom.js';

export class VideoPlayer {
  constructor(cursoId) {
    this.cursoId = cursoId;
    this.players = {};
    this.progressIntervals = {};
    this.videoProgressData = {};

    this.init();
  }

  async init() {
    await this.loadInitialProgress();
    this.initializePlayers();
    this.setupProgressCheckboxes();
  }

  /**
   * Carga el progreso inicial desde el servidor
   */
  async loadInitialProgress() {
    try {
      const data = await api.get('/get_progreso_curso', { curso_id: this.cursoId });

      if (data.success) {
        data.secciones.forEach(seccion => {
          this.videoProgressData[seccion.id] = seccion.progreso || 0;
          this.updateVideoProgressUI(seccion.id, seccion.progreso);
        });
        this.updateCourseProgressUI();
      }
    } catch (error) {
      console.error('Error cargando progreso inicial:', error);
    }
  }

  /**
   * Calcula el progreso total del curso
   */
  calculateTotalProgress() {
    const totalSections = DOM.$$('[id^="seccion-"]').length;
    if (totalSections === 0) return 0;

    let totalProgress = 0;
    for (const seccionId in this.videoProgressData) {
      totalProgress += this.videoProgressData[seccionId];
    }

    return Math.round(totalProgress / totalSections);
  }

  /**
   * Actualiza la UI del progreso del curso
   */
  updateCourseProgressUI() {
    const totalProgress = this.calculateTotalProgress();
    const progressFill = DOM.$('.curso-progreso-fill');
    const progressText = DOM.$('.curso-progreso-texto');

    if (progressFill) {
      progressFill.style.width = `${totalProgress}%`;
    }

    if (progressText) {
      progressText.textContent = `${totalProgress}% completado`;
    }
  }

  /**
   * Actualiza la UI del progreso del video
   */
  updateVideoProgressUI(seccionId, porcentaje) {
    const progressFill = DOM.$(`#progreso-video-${seccionId}`);
    const progressText = DOM.$(`#texto-progreso-${seccionId}`);
    const checkbox = DOM.$(`#completado-${seccionId}`);

    if (progressFill) {
      progressFill.style.width = `${porcentaje}%`;
      progressFill.style.backgroundColor = porcentaje >= 95 ? '#2E7D32' : '#4CAF50';
    }

    if (progressText) {
      progressText.textContent = `${Math.round(porcentaje)}% visto`;
    }

    if (checkbox) {
      checkbox.checked = porcentaje >= 95;
    }

    this.videoProgressData[seccionId] = porcentaje;
    this.updateCourseProgressUI();
  }

  /**
   * Actualiza el progreso en el servidor
   */
  async updateServerProgress(seccionId, porcentaje) {
    try {
      const data = await api.post('/actualizar_progreso_seccion', {
        seccion_id: seccionId,
        curso_id: this.cursoId,
        porcentaje: Math.round(porcentaje)
      });

      if (data && data.success) {
        console.log('Progreso guardado:', data);
      }
    } catch (error) {
      console.error('Error guardando progreso:', error);
    }
  }

  /**
   * Configura los checkboxes de progreso manual
   */
  setupProgressCheckboxes() {
    DOM.$$('.video-completado').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        const seccionId = e.target.id.split('-')[1];
        const porcentaje = e.target.checked ? 100 : 0;

        this.updateVideoProgressUI(seccionId, porcentaje);
        this.updateServerProgress(seccionId, porcentaje);
      });
    });
  }

  /**
   * Configura un reproductor de video HTML5
   */
  setupVideoPlayer(video) {
    const seccionId = video.id.split('-')[1];

    video.addEventListener('timeupdate', () => {
      const porcentaje = (video.currentTime / video.duration) * 100;
      this.updateVideoProgressUI(seccionId, porcentaje);

      // Guardar progreso cada 10%
      if (Math.floor(porcentaje) % 10 === 0) {
        this.updateServerProgress(seccionId, porcentaje);
      }
    });

    video.addEventListener('ended', () => {
      this.updateVideoProgressUI(seccionId, 100);
      this.updateServerProgress(seccionId, 100);
    });
  }

  /**
   * Inicializa todos los reproductores
   */
  initializePlayers() {
    // Para videos HTML5 (archivos locales)
    DOM.$$('video[id^="video-"]').forEach(video => {
      this.setupVideoPlayer(video);
    });

    // Para iframes (YouTube, Vimeo, etc.)
    DOM.$$('iframe[id^="video-"]').forEach(iframe => {
      const seccionId = iframe.id.split('-')[1];
      console.log(`Video iframe cargado para sección ${seccionId}`);
    });
  }
}
