/**
 * Course View Page Module
 * Lógica para la página de visualización de curso
 */

import { VideoPlayer } from '../components/video-player.js';
import { Modal } from '../components/modals.js';
import { DOM } from '../utils/dom.js';

export class CourseViewPage {
  constructor() {
    this.cursoId = this.getCursoId();
    this.videoPlayer = null;
    this.certificadoModal = null;

    this.init();
  }

  init() {
    if (!this.cursoId) {
      console.warn('Curso ID no encontrado');
      return;
    }

    this.setupVideoPlayer();
    this.setupCertificateModal();
  }

  /**
   * Obtiene el ID del curso desde el DOM o URL
   */
  getCursoId() {
    // Intentar obtener de data attribute
    const cursoElement = DOM.$('[data-curso-id]');
    if (cursoElement) {
      return parseInt(cursoElement.getAttribute('data-curso-id'));
    }

    // Intentar obtener de variable global (inyectada por template)
    if (window.cursoId) {
      return window.cursoId;
    }

    // Intentar obtener de URL
    const match = window.location.pathname.match(/\/curso\/(\d+)/);
    return match ? parseInt(match[1]) : null;
  }

  /**
   * Configura el reproductor de video y tracking
   */
  setupVideoPlayer() {
    this.videoPlayer = new VideoPlayer(this.cursoId);
  }

  /**
   * Configura el modal de certificado
   */
  setupCertificateModal() {
    const btnVerCertificado = DOM.$('#btn-ver-certificado');
    const modalCertificado = DOM.$('#modal-certificado');
    const cerrarModal = DOM.$('#cerrar-modal');

    if (!btnVerCertificado || !modalCertificado) return;

    this.certificadoModal = new Modal('modal-certificado');

    btnVerCertificado.addEventListener('click', () => {
      this.certificadoModal.open();
    });

    cerrarModal.addEventListener('click', () => {
      this.certificadoModal.close();
    });

    // Cerrar al hacer click fuera
    modalCertificado.addEventListener('click', (e) => {
      if (e.target === modalCertificado) {
        this.certificadoModal.close();
      }
    });

    // Botón descargar certificado
    const btnDescargar = DOM.$('#btn-descargar-certificado');
    if (btnDescargar) {
      btnDescargar.addEventListener('click', () => {
        this.downloadCertificate();
      });
    }
  }

  /**
   * Descarga el certificado
   */
  downloadCertificate() {
    // TODO: Implementar generación y descarga de certificado PDF
    console.log('Descargando certificado...');
    alert('Funcionalidad de descarga de certificado en desarrollo');
  }
}

// Auto-inicialización
DOM.ready(() => {
  if (document.body.classList.contains('page-course-view') ||
      window.location.pathname.includes('/curso/')) {
    new CourseViewPage();
  }
});
