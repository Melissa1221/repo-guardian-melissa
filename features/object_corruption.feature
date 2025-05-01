Feature: Object corruption detection
  As a repository maintainer
  I want to detect corrupted Git objects
  So that I can repair them before they cause problems

  Scenario: Blob dañado en packfile
    Given un repositorio con packfile "fixtures/pack-corrupt.git"
    When ejecuto "guardian scan fixtures/pack-corrupt.git"
    Then el exit code es 2
    And la salida contiene "Invalid CRC at offset" 