/** @file string-len-max.h
 *  @brief Define maximum lengths for strings for contam-x-cosim API.
 *  @author Brian J. Polidoro (NIST)
 *  @author W. Stuart Dols (NIST)
 *  @date 2023-05-30
 *
 */

#ifndef _STRING_LEN_MAX_H_
#define _STRING_LEN_MAX_H_


#include <limits.h>
#include <stdio.h>
#include <stdlib.h>


//--- Preprocessor definitions.
#define LINELEN 4096    /**< TODO wsd - this was 256 but issues with getcwd() in contam-x-main on Linux where MAX_PATH = 4096 */
#define NOTELEN 72      /**< Description field length for many data structures */
#define NAMEMAXLEN   40 /**< Maximum length of a name allowed to be entered via ContamW */
#define NAMEFIELDLEN 48 /**< Size of a name field to allow for AHS zone/path naming to include (SUP) or (REC) */
#define UNITSTR 16      /**< Size of a field for unit strings */
#define LOGHEADER 32    /**< Size of header for the controls LOG file */
#define HDRLEN 256      /**< Maximum length of header for an output variable */
//
#ifndef _MAX_PATH       // Windows/DOS defined in <stdlib.h> */

# ifdef PATH_MAX               // GNUC parameter defined in <limits.h>
#  define _MAX_PATH  PATH_MAX  // PATH_MAX = max bytes in a pathname
#  define _MAX_DIR   PATH_MAX
# elif defined FILENAME_MAX    // Should always be defined in <stdio.h>
#  define _MAX_PATH  FILENAME_MAX
#  define _MAX_DIR   FILENAME_MAX
# else
#  define _MAX_PATH  260       // VisualC++ value
#  define _MAX_DIR   256       // VisualC++ value
# endif  // End #ifdef PATH_MAX.

# ifdef NAME_MAX               // GNUC parameter defined in <limits.h>
#  define _MAX_FNAME NAME_MAX  // NAME_MAX = max bytes in a filename
# elif defined FILENAME_MAX    // Should always be defined in <stdio.h>
#  define _MAX_FNAME FILENAME_MAX
# else
#  define _MAX_FNAME 256       // VisualC++ value
# endif  // End #ifdef NAME_MAX.

# define _MAX_DRIVE 4    // 3 minimum (3 VisualC++)
# define _MAX_EXT   8    // 5 minimum (256 VisualC++)

#endif  // End #ifndef _MAX_PATH

#endif  // End #ifndef _STRING_LEN_MAX_H_.
